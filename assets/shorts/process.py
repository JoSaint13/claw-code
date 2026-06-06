import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

files = {
    "f1_hyped.png": "f1_t.png",
    "f2_happy.png": "f2_t.png",
    "f3_tired.png": "f3_t.png",
    "f4_out.png":   "f4_t.png",
}

for src, dst in files.items():
    im = Image.open(src).convert("RGBA")
    arr = np.array(im)
    rgb = arr[:, :, :3].astype(np.int16)
    # near-white background candidate
    white = (rgb.min(axis=2) > 228)
    # label connected white regions (8-connectivity)
    structure = np.ones((3, 3), dtype=int)
    labels, n = ndimage.label(white, structure=structure)
    # labels touching the image border == outer background
    border = set(labels[0, :]) | set(labels[-1, :]) | set(labels[:, 0]) | set(labels[:, -1])
    border.discard(0)
    bg_mask = np.isin(labels, list(border))
    alpha = arr[:, :, 3].copy()
    alpha[bg_mask] = 0
    arr[:, :, 3] = alpha
    out = Image.fromarray(arr, "RGBA")
    # feather the alpha edge slightly to kill the white halo / hard jaggies
    a = out.split()[3].filter(ImageFilter.GaussianBlur(0.8))
    out.putalpha(a)
    out.save(dst)
    cov = 100.0 * bg_mask.sum() / bg_mask.size
    print(f"{src} -> {dst}: removed {cov:.1f}% as background, regions={n}")
