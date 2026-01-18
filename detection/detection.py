import cv2 as cv
from ultralytics import YOLO
import time
import collections
import threading
import queue
import os

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
        save_queue.task_done()

thread = threading.Thread(target=save_worker, daemon=True)
thread.start()

model = YOLO(r'model\people.pt')
CONFIDENCE_THRESHOLD = 0.8

VID_WIDTH, VID_HEIGHT = 1280, 720
FRAME_SIZE = (VID_WIDTH, VID_HEIGHT)
capture = cv.VideoCapture(0)
capture.set(cv.CAP_PROP_FRAME_WIDTH, VID_WIDTH)
capture.set(cv.CAP_PROP_FRAME_HEIGHT, VID_HEIGHT)

FPS = 30
FRAME_TIME = 1/ FPS

BUFFER_SECONDS = 60
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

    # Draw bounding boxes on the annotated frame
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
        confidences = result.boxes.conf.cpu().numpy()
        class_ids = result.boxes.cls.cpu().numpy()

        for box, conf, cls in zip(boxes, confidences, class_ids):
            if conf < CONFIDENCE_THRESHOLD:
                continue
            x1, y1, x2, y2 = map(int, box)
            label = f"{int(cls)}:{conf:.2f}"

            cv.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv.putText(annotated_frame, label, (x1, y1 - 10),
                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    elapsed = time.time() - start_time
    time_to_wait = max(0, FRAME_TIME - elapsed)
    time.sleep(time_to_wait)

    cv.imshow('Video (press q to exit)', annotated_frame)

    key = cv.waitKey(20) & 0xFF

    if key == ord('s'):
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
