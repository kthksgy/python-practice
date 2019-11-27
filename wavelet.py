import cv2
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import convolve2d


def uint8(x):
    x = np.where(x > 255, 255, x)
    x = np.where(x < 0, 0, x)
    return x.astype(np.uint8)


def dwt2d(x, lk, hk, nl=3):
    if len(x.shape) == 2:
        x = np.expand_dims(x, -1)
    ret = np.zeros(x.shape)
    src = x
    w = x.shape[1]
    h = x.shape[0]
    for l in range(nl):
        print('Level', l)
        for i, c in enumerate(src.transpose(2, 0, 1)):
            ll = convolve2d(c, np.expand_dims(lk, 0), 'same', 'symm')
            ll = convolve2d(ll, np.expand_dims(lk, -1), 'same', 'symm')
            ret[0:h//2, 0:w//2, i] = ll[::2, ::2]

            hl = convolve2d(c, np.expand_dims(lk, 0), 'same', 'symm')
            hl = convolve2d(hl, np.expand_dims(hk, -1), 'same', 'symm')
            ret[0:h//2, w//2:w, i] = hl[::2, 1::2]

            lh = convolve2d(c, np.expand_dims(hk, 0), 'same', 'symm')
            lh = convolve2d(lh, np.expand_dims(lk, -1), 'same', 'symm')
            ret[h//2:h, 0:w//2, i] = lh[1::2, ::2]

            hh = convolve2d(c, np.expand_dims(hk, 0), 'same', 'symm')
            hh = convolve2d(hh, np.expand_dims(hk, -1), 'same', 'symm')
            ret[h//2:h, w//2:w, i] = hh[1::2, 1::2]

        src = np.copy(ret[0:h//2, 0:w//2])
        h = h // 2
        w = w // 2
        
        print(src.shape)
    return ret

LCOEF_5_3 = np.asarray([
     6 / 8,
     2 / 8,
    -1 / 8,
])
LCOEF_5_3 = np.append(np.flip(LCOEF_5_3)[:-1], LCOEF_5_3)

HCOEF_5_3 = np.asarray([
    1,
    -1 / 2
])
HCOEF_5_3 = np.append(np.flip(HCOEF_5_3)[:-1], HCOEF_5_3)

LCOEF_9_7 = np.asarray([
    0.6029490182363579,
    0.2668641184428723,
    -0.07822326652898785,
    -0.01686411844287495,
    0.02674875741080976
])
LCOEF_9_7 = np.append(np.flip(LCOEF_9_7)[:-1], LCOEF_9_7)

HCOEF_9_7 = np.asarray([
    1.115087052456994,
    -0.5912717631142470,
    -0.05754352622849957,
    0.09127176311424948
])
HCOEF_9_7 = np.append(np.flip(HCOEF_9_7)[:-1], HCOEF_9_7)

src = cv2.imread('campus.png')
src = cv2.resize(src, (400, 400))
src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
# src = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
# src = cv2.cvtColor(src, cv2.COLOR_RGB2YCrCb)
src = src.astype(np.float32)

# h, w, c
# src = np.arange(192).reshape((8, 3, 8)).transpose(0, 2, 1)

dst = dwt2d(src, LCOEF_9_7, HCOEF_9_7, 4)
#dst = dst.astype(np.uint8)
#dst = cv2.cvtColor(dst, cv2.COLOR_YCrCb2RGB)
dst = uint8(dst)
# dst = cv2.equalizeHist(dst)

plt.imshow(np.squeeze(dst), cmap='gray')
plt.show()
