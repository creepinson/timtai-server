from typing import Tuple
import cv2
import numpy as np


def replace_img(
    img: np.ndarray,
    replacement_img: np.ndarray,
    pos: Tuple[int],
):
    (x, y, w, h) = pos
    target: np.ndarray = cv2.resize(replacement_img, (w, h))
    if len(target.shape) == len(img.shape):
        img[y : y + target.shape[0], x : x + target.shape[1], :] = target
    return img
