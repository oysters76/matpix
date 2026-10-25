import numpy as np
from PIL import Image


def cartesian_to_pixel(cx, cy, height):
    px = cx
    py = height - 1 - cy
    return px, py


def pixel_to_cartesian(px, py, height):
    cx = px
    cy = height - 1 - py
    return cx, cy


def mat_transform_png(filename, transform_mat, output_name, verbose_callback=None):
    img = Image.open(filename)
    pixels_org = np.array(img)

    det = np.linalg.det(transform_mat)
    scale_factor = abs(det)

    if scale_factor == 0:
        raise ValueError("Bad matrix — determinant is zero")

    h, w, channels = pixels_org.shape

    if verbose_callback:
        verbose_callback(f"Opened {filename}: {w}x{h}, {channels} channels")

    corners = np.array([[0, 0], [w - 1, 0], [0, h - 1], [w - 1, h - 1]])
    transformed_corners = np.array([transform_mat @ c for c in corners])
    min_xy = transformed_corners.min(axis=0)
    max_xy = transformed_corners.max(axis=0)

    sw = round(max_xy[0] - min_xy[0]) + 1
    sh = round(max_xy[1] - min_xy[1]) + 1
    offset_x = round(min_xy[0])
    offset_y = round(min_xy[1])

    if verbose_callback:
        verbose_callback(f"Output size: {sw}x{sh}, offset: ({offset_x}, {offset_y})")

    pixels_transformed = np.zeros((sh, sw, channels), dtype=np.uint8)

    for py in range(h):
        for px in range(w):
            cx, cy = pixel_to_cartesian(px, py, h)
            v = np.array([cx, cy])

            transformed = transform_mat @ v
            t_cx = round(transformed[0]) - offset_x
            t_cy = round(transformed[1]) - offset_y

            t_px, t_py = cartesian_to_pixel(t_cx, t_cy, sh)

            if 0 <= t_px < sw and 0 <= t_py < sh:
                pixels_transformed[t_py, t_px] = pixels_org[py, px]

        if verbose_callback and (py + 1) % 100 == 0:
            verbose_callback(f"Processing row {py + 1}/{h}")

    if verbose_callback:
        verbose_callback(f"Processing row {h}/{h}")

    transformed_img = Image.fromarray(pixels_transformed)
    transformed_img.save(output_name)

    if verbose_callback:
        verbose_callback(f"Saved to {output_name}")
