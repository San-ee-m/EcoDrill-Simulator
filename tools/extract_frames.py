import cv2
import os

video_path = "rig_drill.mp4" # This was the name of the video that got extracted
output_folder = "RigDrillFrames" 

os.makedirs(output_folder, exist_ok=True)

cap = cv2.VideoCapture(video_path)
frame_num = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imwrite(f"{output_folder}/frame_{frame_num:03d}.png", frame)
    frame_num += 1

cap.release()

print("Done:", frame_num, "frames")
