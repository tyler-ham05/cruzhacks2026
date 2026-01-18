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

UID = 'google-oauth2|112660930199868117288'

def save_first_frame(frames, output_path):
    if not frames:
        print("⚠️ No frames provided, cannot save first frame.")
        return False

    first_frame = frames[0]

    success = cv.imwrite(output_path, first_frame)

    if not success:
        print(f"❌ Failed to save first frame to {output_path}")
        return False

    print(f"✅ Saved first frame to {output_path}")
    return True


def point_in_bbox(x, y, bbox):
    x1, y1, x2, y2 = bbox
    return x1 <= x <= x2 and y1 <= y <= y2

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

        output.severity = 3
        
        if output.severity != 0:
            asset_id = GMux.uploadToMux(output_path)

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            data = {
                "userID": UID,
                "videoURL": asset_id,
                "timestamp": timestamp,
                "summary": output.summary,
                "severity": output.severity,
                "extended_summary": output.extended_summary,
                "incidentType": output.incident_type,
            }

            url = "https://cruzhacks2026server.vercel.app/api"
            response = requests.post(url, json=data)

            if not response.ok:
                print("Database request failed")

        folder_path = os.path.join("clips/")

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            if os.path.isfile(file_path):
                os.remove(file_path)
        save_queue.task_done()

thread = threading.Thread(target=save_worker, daemon=True)
thread.start()

cur_path = os.path.join('model', 'best.pt')

print("CWD:", os.getcwd())
print("Exists?", os.path.exists(cur_path))

model = YOLO(cur_path)
CONFIDENCE_THRESHOLD = 0.8

tracker = DeepSort(max_age=30)
bbox1 = (120, 180, 360, 620)
bbox2 = (780, 160, 1050, 640)

track_history = {}   # track_id -> list[(x,y)]
counted_tracks = set() #might be unecessary

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

event = False

track_entered_bbox1 = set()
track_entered_bbox2 = set()

while True:
    start_time = time.time()

    ret, frame = capture.read()
    if not ret:
        continue

    frame_buffer.append(frame)

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
    cv.rectangle(frame, (bbox1[0], bbox1[1]), (bbox1[2], bbox1[3]), (0, 255, 0), 2)
    cv.rectangle(frame, (bbox2[0], bbox2[1]), (bbox2[2], bbox2[3]), (0, 0, 255), 2)

    cv.putText(
        frame,
        "Entrance",
        (bbox1[0], bbox1[1] - 10),
        cv.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

    cv.putText(
        frame,
        "Exit",
        (bbox2[0], bbox2[1] - 10),
        cv.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 255),
        2
    )



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

        in_bbox1 = point_in_bbox(cx, cy, bbox1)
        in_bbox2 = point_in_bbox(cx, cy, bbox2)

        # Mark if this track has ever entered bbox1
        if in_bbox1:
            track_entered_bbox1.add(track_id)

        # Detect entering bbox2
        if in_bbox2 and track_id not in track_entered_bbox2:
            track_entered_bbox2.add(track_id)

            # 🚨 Trigger event if they never entered bbox1
            if track_id not in track_entered_bbox1:
                event = True
                print(f"⚠️ ALERT: ID {track_id} entered bbox2 without entering bbox1")

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
        event = False

    if key == ord('q'):
        break


capture.release()

save_first_frame(list(frame_buffer), "clips/clip_0.jpg")

cv.destroyAllWindows()

save_queue.put(None)
thread.join()
