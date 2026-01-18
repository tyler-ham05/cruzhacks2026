import cv2 as cv
from ultralytics import YOLO
import time
import collections
import threading
import queue
import os
from GeminiMux import IncidentReport
import GeminiMux as GMux
from deep_sort_realtime.deepsort_tracker import DeepSort
import subprocess
import requests
import datetime

os.makedirs('clips', exist_ok=True)

save_queue = queue.Queue()


def save_worker():
    """Worker thread that saves clips from the queue."""
    while True:
        item = save_queue.get()

        if item is None:
            break
        frames, output_path, fps, frame_size = item
        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        out = cv.VideoWriter(output_path, fourcc, fps, frame_size)
        if not out.isOpened():
            print(f"Error: Could not open VideoWriter for path {output_path}")
            continue
        for frame in frames:
            if (frame.shape[1], frame.shape[0]) != frame_size:
                frame = cv.resize(frame, frame_size)
            out.write(frame)
        
        out.release()
        print(f"Saved video clip to {output_path}")

        output = GMux.clipProcessing(output_path)

        asset_id = GMux.uploadToMux(output_path)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = {
            "videoURL": asset_id,
            "timestamp": timestamp,
            "summary": output.summary,
            "severity": output.severity,
            "incidentType": output.incident_type,
        }

        url = "https://localhost3000"
        response = requests.post(url, data)

        if not response.ok:
            print("Database request failed")

        save_queue.task_done()

thread = threading.Thread(target=save_worker, daemon=True)
thread.start()

cur_path = os.path.join('model', 'best.pt')

print("CWD:", os.getcwd())
print("Exists?", os.path.exists(cur_path))

model = YOLO(cur_path)
CONFIDENCE_THRESHOLD = 0.8

tracker = DeepSort(max_age=30)
#LINE_Y = 300
LINE_X = 960

track_history = {}   # track_id -> list[(x,y)]
counted_tracks = set() #might be unecessary

enter_count = 0
exit_count = 0

VID_WIDTH, VID_HEIGHT = 1280, 720
FRAME_SIZE = (VID_WIDTH, VID_HEIGHT)
capture = cv.VideoCapture(0)
capture.set(cv.CAP_PROP_FRAME_WIDTH, VID_WIDTH)
capture.set(cv.CAP_PROP_FRAME_HEIGHT, VID_HEIGHT)

FPS = 15
FRAME_TIME = 1/ FPS

BUFFER_SECONDS = 10
BUFFER_SIZE = int(FPS * BUFFER_SECONDS)
frame_buffer = collections.deque(maxlen=BUFFER_SIZE)

while True:
    start_time = time.time()

    ret, frame = capture.read()
    if not ret:
        continue

    frame_buffer.append(frame)

    annotated_frame = frame.copy()

    results = model(frame, verbose=False)
            
    detections = []

    # Draw bounding boxes
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
        confidences = result.boxes.conf.cpu().numpy()
        class_ids = result.boxes.cls.cpu().numpy()

        for box, conf, cls in zip(boxes, confidences, class_ids):
            if (conf < CONFIDENCE_THRESHOLD): 
                continue
            x1, y1, x2, y2 = map(int, box)
            label = f"{int(cls)}:{conf:.2f}"

            w_box = x2-x1

            h_box = y2-y1

            detections.append(([x1, y1, w_box, h_box], conf, "person"))

            # cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # cv.putText(frame, label, (x1, y1 - 10),
            #            cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    tracks = tracker.update_tracks(detections, frame=frame)

    #cv.line(frame, (0, LINE_Y), (frame.shape[1], LINE_Y), (255, 0, 0), 2)
    cv.line(frame, (LINE_X, 0), (LINE_X, frame.shape[0]), (255, 0, 0), 2)

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        l, t, r, b = track.to_ltrb()

        cx = int((l + r) / 2)
        cy = int((t + b) / 2)

        # Store history
        if track_id not in track_history:
            track_history[track_id] = []
        track_history[track_id].append((cx, cy))

        # -----------------------------
        # Direction logic
        # -----------------------------
        if len(track_history[track_id]) >= 2 and track_id not in counted_tracks:
            # prev_y = track_history[track_id][-2][1]
            # curr_y = track_history[track_id][-1][1]

            prev_x = track_history[track_id][-2][0]
            curr_x = track_history[track_id][-1][0]

            # Crossing upward = EXIT
            # elif prev_y >= LINE_Y and curr_y < LINE_Y:
            #     exit_count += 1
            #     counted_tracks.add(track_id)
            #     print(f"EXIT: ID {track_id}")
            
            if prev_x >= LINE_X and curr_x < LINE_X:
                exit_count += 1
                event = True
                counted_tracks.add(track_id)
                print(f"EXIT: ID {track_id}")

        # -----------------------------
        # Visualization
        # -----------------------------
        cv.rectangle(
            frame,
            (int(l), int(t)),
            (int(r), int(b)),
            (0, 255, 0),
            2
        )

        cv.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

        cv.putText(
            frame,
            f"ID {track_id}",
            (int(l), int(t) - 10),
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    cv.imshow('Video (press q to exit)', frame)

    elapsed = time.time() - start_time
    time_to_wait = max(0, FRAME_TIME - elapsed)
    time.sleep(time_to_wait)

    key = cv.waitKey(20) & 0xFF

    if event:
        clip_frames = list(frame_buffer)
        timestamp = int(time.time())
        output_filename = f'clips/clip_{timestamp}.mp4'
        save_queue.put((clip_frames, output_filename, FPS, FRAME_SIZE))

    if key == ord('q'):
        break


capture.release()
cv.destroyAllWindows()

save_queue.put(None)
thread.join()
