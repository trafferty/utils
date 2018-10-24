import cv2
import numpy as np
from matplotlib import pyplot as plt
import time


def adaptive_thresh(input_img):
    h, w = input_img.shape

    S = int(w/8)
    s2 = int(S/2)
    T = 15.0

    #integral img
    int_img = np.zeros_like(input_img, dtype=np.int64)
    for col in range(w):
        for row in range(h):
            int_img[row,col] = input_img[0:row,0:col].sum()

    #output img
    out_img = np.zeros_like(input_img)    
    for col in range(w):
        for row in range(h):
            #SxS region
            y0 = max(row-s2, 0)
            y1 = min(row+s2, h-1)
            x0 = max(col-s2, 0)
            x1 = min(col+s2, w-1)

            count = (y1-y0)*(x1-x0)

            try:
                sum_ = int_img[y1, x1]-int_img[y0, x1]-int_img[y1, x0]+int_img[y0, x0]
            except:
                print(x0)
                print(x1)
                print(y0)
                print(y1)
                raise()


            if input_img[row, col]*count < sum_*(100.-T)/100.:
                out_img[row,col] = 0
            else:
                out_img[row,col] = 255

    return out_img

jd = cv2.imread('/Users/trafferty/tmp/DIF/just_drops_DIF2_1262x631_8bit.png', cv2.IMREAD_GRAYSCALE)
print(jd.dtype)

start = time.time()
out_img = adaptive_thresh(jd)
end = time.time()

print(f"done, now plotting. Took {end-start} secs...")
#util.plot_imgs([( jd, "jd"), ( out_img, "out_img")], fig_size=20)
fig, axes = plt.subplots(nrows= 1, ncols=2, squeeze=True, figsize=(18,(5*1)))
ax1 = axes[0]
ax2 = axes[1]
ax1.imshow(jd, cmap='gray',interpolation='nearest', aspect='equal')
ax1.axis('off')
ax1.set_title("jd")
ax2.imshow(out_img, cmap='gray',interpolation='nearest', aspect='equal')
ax2.axis('off')
ax2.set_title("out_img")
plt.show()
