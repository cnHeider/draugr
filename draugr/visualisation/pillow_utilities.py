#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 17/07/2020
           """

from typing import Tuple, Union

import numpy
from PIL import Image

__all__ = [
    "pil_merge_images",
    "pil_img_to_np_array",
    "np_array_to_pil_img",
    "pil_image_to_byte_array",
    "byte_array_to_pil_image",
]

import io

from PIL import Image


def pil_image_to_byte_array(image: Image.Image, *, coding: str = "PNG") -> bytes:
    """
  PNG encoded by default
  @param coding:
  @param image:
  @return:
  """
    buffer = io.BytesIO()
    image.save(buffer, coding)
    return buffer.getvalue()


def byte_array_to_pil_image(byte_array: bytes) -> Image.Image:
    """

  @param byte_array:
  @return:
  """
    return Image.open(io.BytesIO(byte_array))


def pil_img_to_np_array(
    data_path: Union[str, Image.Image],
    *,
    desired_size: Tuple[int, int] = None,
    expand: int = False
) -> numpy.ndarray:
    """
  Util function for loading RGB image into a numpy array.

  Returns array of shape (1, H, W, C)."""
    img = Image.open(data_path)
    img = img.convert("RGB")
    if desired_size:
        img = img.resize((desired_size[1], desired_size[0]))
    x = numpy.asarray(img, dtype="float32")
    if expand:
        x = numpy.expand_dims(x, axis=0)
    return x / 255.0


def np_array_to_pil_img(x: numpy.ndarray) -> Image.Image:
    """
  Util function for converting anumpy array to a PIL img.

  Returns PIL RGB img."""
    x = numpy.asarray(x)
    x = x + max(-numpy.min(x), 0)
    x_max = numpy.max(x)
    if x_max != 0:
        x /= x_max
    return Image.fromarray((x * 255.0).astype("uint8"), "RGB")


def pil_merge_images(image1: Image.Image, image2: Image.Image) -> Image.Image:
    """Merge two images into one, displayed side by side."""
    (width1, height1) = image1.size
    (width2, height2) = image2.size

    result_width = width1 + width2
    result_height = max(height1, height2)

    result = Image.new("RGB", (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(width1, 0))
    return result
