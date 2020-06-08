
import cv2
import numpy as np
from matplotlib import pyplot as plt

fname = '/Users/trafferty/tmp/MilSequence_20200429_Test11.avi'

cap = cv2.VideoCapture(fname)
fps = cap.get(cv2.CAP_PROP_FPS)
print("FPS=", fps)

timestamps = [cap.get(cv2.CAP_PROP_POS_MSEC)]
calc_timestamps = [0.0]

frame_cnt = 0
print("Now processing video frame-by-frame")
while(cap.isOpened()):
    frame_exists, curr_frame = cap.read()
    if frame_exists:
        timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC))
        calc_timestamps.append(calc_timestamps[-1] + 1000/fps)
        frame_cnt += 1
    else:
        break

cap.release()

frame_diffs = []
for i, (ts, cts) in enumerate(zip(timestamps, calc_timestamps)):
    frame_diffs.append(abs(ts - cts))
    #print('Frame %d difference:'%i, abs(ts - cts))

print("Processed %d frames" % frame_cnt)

'''
    Calc the deltas between actual and calculated frame timestamps
    Then plot...
'''
frame_start = 0
frame_end = frame_cnt
x_range = [x for x in range(frame_start, frame_end, 1)]

frame_diffs_part_np = np.array(frame_diffs[frame_start:frame_end])
plt.figure(1, figsize=(25,5))
plt.plot(x_range, frame_diffs_part_np)
plt.ylabel("Timestamp Delta (msec)")
plt.xlabel("Frame number")
plt.title("Frame-to-frame Timestamps: Actual vs Calculated")
#plt.show()

'''
    Find the deltas between the actual timestamps
    Then plot...
'''
deltas = []
for i, ts in enumerate(timestamps):
    if i == 0:
        prev = ts
        continue
    else:
        deltas.append(abs(ts - prev))
        prev = ts

deltas_np = np.array(deltas)
print(f"Deltas mean: {np.mean(deltas_np)}")
print(f"Deltas max: {np.max(deltas_np)}")
print(f"Deltas min: {np.min(deltas_np)}")
print(f"Deltas std: {np.std(deltas_np)}")

plt.figure(2, figsize=(25,5))
plt.plot(deltas_np)
plt.ylabel('Frame Delta (msec)')
plt.xlabel('Frame number')
plt.title("Frame-to-frame Timestamp Deltas")
#plt.show()


'''
    Something weird going on at the end.
    Plot the last 150 pts
'''
frame_start = frame_cnt - 150
frame_end = frame_cnt
x_range = [x for x in range(frame_start, frame_end, 1)]

deltas_end_np = np.array(deltas[frame_start:frame_end])
plt.figure(3, figsize=(25,5))
plt.plot(x_range,deltas_end_np)
plt.ylabel('Frame Delta (msec)')
plt.xlabel('Frame number')
plt.title("Frame-to-frame Timestamp Deltas: Frames %d - %d" % (frame_start, frame_end))
#plt.show()


'''
    Plot the area that Tomo was interested in seeing
'''
frame_start = 900
frame_end = 1000
x_range = [x for x in range(frame_start, frame_end, 1)]

deltas_range_np = np.array(deltas[frame_start:frame_end])
plt.figure(4, figsize=(25,5))
plt.plot(x_range,deltas_range_np)
plt.ylabel('Frame Delta (msec)')
plt.xlabel('Frame number')
plt.ylim(np.min(deltas_range_np)-1,np.min(deltas_range_np)+1)
plt.title("Frame-to-frame Timestamp Deltas: Frames %d - %d" % (frame_start, frame_end))

plt.show()


