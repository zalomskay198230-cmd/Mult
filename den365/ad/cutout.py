"""вырезает персонажа со светлого градиентного фона: фон — гладкие области, связанные с краем картинки"""
import sys
from PIL import Image, ImageFilter
import numpy as np
from scipy import ndimage as ndi

src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
g = np.zeros(a.shape[:2], np.float32)
for c in range(3):
    ch = ndi.gaussian_filter(a[:, :, c], 1.0)
    g = np.maximum(g, np.hypot(ndi.sobel(ch, 0), ndi.sobel(ch, 1)))
low = g < 14
lab, n = ndi.label(low)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(border))
bg = ndi.binary_dilation(bg, iterations=2) & (g < 40)
fg = ndi.binary_fill_holes(ndi.binary_opening(~bg, iterations=2))
lab2, n2 = ndi.label(fg)
sizes = ndi.sum(fg, lab2, range(1, n2 + 1))
fg = lab2 == 1 + int(np.argmax(sizes))
alpha = Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))
out = im.convert("RGBA"); out.putalpha(alpha)
out.crop(alpha.getbbox()).save(dst)
