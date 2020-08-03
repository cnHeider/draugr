import types
from typing import Any, List, Tuple

import cv2
import numpy
import torch
from PIL.ImageTransform import Transform
from numpy import random

__all__ = [
    "CV2Compose",
    "Lambda",
    "ConvertFromInts",
    "SubtractMeans",
    "CV2ToAbsoluteCoords",
    "CV2ToPercentCoords",
    "CV2Resize",
    "CV2RandomSaturation",
    "CV2RandomHue",
    "CV2RandomLightingNoise",
    "CV2ConvertColor",
    "CV2RandomContrast",
    "CV2RandomBrightness",
    "CV2ToImage",
    "CV2ToTensor",
    "CV2RandomSampleCrop",
    "CV2Expand",
    "CV2RandomMirror",
    "CV2SwapChannels",
    "CV2PhotometricDistort",
]

from draugr.opencv_utilities.bounding_boxes.colors import Triple
from draugr.opencv_utilities.bounding_boxes.evaluation import (
    jaccard_overlap_numpy,
    remove_null_boxes,
)


class CV2Compose(object):
    """Composes several augmentations together.
Args:
transforms (List[Transform]): list of transforms to compose.
Example:
>>> augmentations.Compose([
>>>     transforms.CenterCrop(10),
>>>     transforms.ToTensor(),
>>> ])
"""

    def __init__(self, transforms: List[Transform]):
        self._transforms = transforms

    def __call__(self, img, boxes=None, labels=None) -> Tuple:
        for transform in self._transforms:
            img, boxes, labels = transform(img, boxes, labels)
            if boxes is not None:
                boxes, labels = remove_null_boxes(boxes, labels)
        return img, boxes, labels


class Lambda(object):
    """Applies a lambda as a transform."""

    def __init__(self, lambd: callable):
        assert isinstance(lambd, types.LambdaType)
        self.lambd = lambd

    def __call__(self, img: Any, boxes: Any = None, labels: Any = None):
        return self.lambd(img, boxes, labels)


class ConvertFromInts(object):
    def __call__(self, image: Any, boxes: Any = None, labels: Any = None) -> Tuple:
        return image.astype(numpy.float32), boxes, labels


class SubtractMeans(object):
    def __init__(self, mean: Tuple):
        self.mean = numpy.array(mean, dtype=numpy.float32)

    def __call__(self, image: Any, boxes: Any = None, labels: Any = None) -> Tuple:
        image = image.astype(numpy.float32)
        image -= self.mean
        return image.astype(numpy.float32), boxes, labels


class CV2ToAbsoluteCoords(object):
    def __call__(self, image: Any, boxes: Any = None, labels: Any = None) -> Tuple:
        height, width, channels = image.shape
        boxes[:, 0] *= width
        boxes[:, 2] *= width
        boxes[:, 1] *= height
        boxes[:, 3] *= height

        return image, boxes, labels


class CV2ToPercentCoords(object):
    def __call__(
        self,
        image: numpy.ndarray,
        boxes: numpy.ndarray = None,
        labels: numpy.ndarray = None,
    ) -> Tuple:
        height, width, channels = image.shape
        boxes[:, 0] /= width
        boxes[:, 2] /= width
        boxes[:, 1] /= height
        boxes[:, 3] /= height

        return image, boxes, labels


class CV2Resize(object):
    def __init__(self, size: int = 300):
        self._size = size

    def __call__(
        self,
        image: numpy.ndarray,
        boxes: numpy.ndarray = None,
        labels: numpy.ndarray = None,
    ) -> Tuple:
        image = cv2.resize(image, (self._size, self._size))
        return image, boxes, labels


class CV2RandomSaturation(object):
    def __init__(self, lower: float = 0.5, upper: float = 1.5):
        self.lower = lower
        self.upper = upper
        assert self.upper >= self.lower, "contrast upper must be >= lower."
        assert self.lower >= 0, "contrast lower must be non-negative."

    def __call__(
        self,
        image: numpy.ndarray,
        boxes: numpy.ndarray = None,
        labels: numpy.ndarray = None,
    ) -> Tuple:
        if random.randint(2):
            image[..., 1] *= random.uniform(self.lower, self.upper)

        return image, boxes, labels


class CV2RandomHue(object):
    def __init__(self, delta: float = 18.0):
        assert delta >= 0.0 and delta <= 360.0
        self.delta = delta

    def __call__(
        self,
        image: numpy.ndarray,
        boxes: numpy.ndarray = None,
        labels: numpy.ndarray = None,
    ) -> Tuple:
        if random.randint(2):
            image[..., 0] += random.uniform(-self.delta, self.delta)
            image[..., 0][image[..., 0] > 360.0] -= 360.0
            image[..., 0][image[..., 0] < 0.0] += 360.0
        return image, boxes, labels


class CV2RandomLightingNoise(object):
    def __init__(self):
        self.perms = ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0))

    def __call__(
        self,
        image: numpy.ndarray,
        boxes: numpy.ndarray = None,
        labels: numpy.ndarray = None,
    ) -> Tuple:
        if random.randint(2):
            swap = self.perms[random.randint(len(self.perms))]
            shuffle = CV2SwapChannels(swap)  # shuffle channels
            image = shuffle(image)
        return image, boxes, labels


class CV2ConvertColor(object):
    def __init__(self, current, transform):
        self.transform = transform
        self.current = current

    def __call__(
        self,
        image: numpy.ndarray,
        boxes: numpy.ndarray = None,
        labels: numpy.ndarray = None,
    ) -> Tuple:
        if self.current == "BGR" and self.transform == "HSV":
            image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        elif self.current == "RGB" and self.transform == "HSV":
            image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        elif self.current == "BGR" and self.transform == "RGB":
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif self.current == "HSV" and self.transform == "BGR":
            image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
        elif self.current == "HSV" and self.transform == "RGB":
            image = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
        else:
            raise NotImplementedError
        return image, boxes, labels


class CV2RandomContrast(object):
    def __init__(self, lower: float = 0.5, upper: float = 1.5):
        self.lower = lower
        self.upper = upper
        assert self.upper >= self.lower, "contrast upper must be >= lower."
        assert self.lower >= 0, "contrast lower must be non-negative."

    # expects float image
    def __call__(
        self,
        image: numpy.ndarray,
        boxes: numpy.ndarray = None,
        labels: numpy.ndarray = None,
    ) -> Tuple:
        if random.randint(2):
            alpha = random.uniform(self.lower, self.upper)
            image *= alpha
        return image, boxes, labels


class CV2RandomBrightness(object):
    def __init__(self, delta: float = 32):
        assert delta >= 0.0
        assert delta <= 255.0
        self.delta = delta

    def __call__(
        self,
        image: numpy.ndarray,
        boxes: numpy.ndarray = None,
        labels: numpy.ndarray = None,
    ) -> Tuple:
        if random.randint(2):
            delta = random.uniform(-self.delta, self.delta)
            image += delta
        return image, boxes, labels


class CV2ToImage(object):
    def __call__(
        self,
        tensor: torch.Tensor,
        boxes: numpy.ndarray = None,
        labels: numpy.ndarray = None,
    ) -> Tuple:
        return (
            tensor.cpu().numpy().astype(numpy.float32).transpose((1, 2, 0)),
            boxes,
            labels,
        )


class CV2ToTensor(object):
    def __call__(
        self,
        cvimage: numpy.ndarray,
        boxes: numpy.ndarray = None,
        labels: numpy.ndarray = None,
    ) -> Tuple:
        return (
            torch.from_numpy(cvimage.astype(numpy.float32)).permute(2, 0, 1),
            boxes,
            labels,
        )


class CV2RandomSampleCrop(object):
    """Crop
Arguments:
img (Image): the image being input during training
boxes (Tensor): the original bounding boxes in pt form
labels (Tensor): the class labels for each bbox
mode (float tuple): the min and max jaccard overlaps
Return:
(img, boxes, classes)
    img (Image): the cropped image
    boxes (Tensor): the adjusted bounding boxes in pt form
    labels (Tensor): the class labels for each bbox
"""

    def __init__(self):
        self.sample_options = (
            # using entire original input image
            None,
            # sample a patch s.t. MIN jaccard w/ obj in .1,.3,.4,.7,.9
            (0.1, None),
            (0.3, None),
            (0.7, None),
            (0.9, None),
            # randomly sample a patch
            (None, None),
        )

    def __call__(
        self,
        image: numpy.ndarray,
        boxes: numpy.ndarray = None,
        labels: numpy.ndarray = None,
    ) -> Tuple:
        # guard against no boxes
        if boxes is not None and boxes.shape[0] == 0:
            return image, boxes, labels
        height, width, _ = image.shape
        while True:
            # randomly choose a mode
            mode = random.choice(self.sample_options)
            if mode is None:
                return image, boxes, labels

            min_iou, max_iou = mode
            if min_iou is None:
                min_iou = float("-inf")
            if max_iou is None:
                max_iou = float("inf")

            # max trails (50)
            for _ in range(50):
                current_image = image

                w = random.uniform(0.3 * width, width)
                h = random.uniform(0.3 * height, height)

                # aspect ratio constraint b/t .5 & 2
                if h / w < 0.5 or h / w > 2:
                    continue

                left = random.uniform(width - w)
                top = random.uniform(height - h)

                # convert to integer rect x1,y1,x2,y2
                rect = numpy.array([int(left), int(top), int(left + w), int(top + h)])

                # calculate IoU (jaccard overlap) b/t the cropped and gt boxes
                overlap = jaccard_overlap_numpy(boxes, rect)

                # is min and max overlap constraint satisfied? if not try again
                if overlap.max() < min_iou or overlap.min() > max_iou:
                    continue

                # cut the crop from the image
                current_image = current_image[rect[1] : rect[3], rect[0] : rect[2], :]

                # keep overlap with gt box IF center in sampled patch
                centers = (boxes[:, :2] + boxes[:, 2:]) / 2.0

                # mask in all gt boxes that above and to the left of centers
                m1 = (rect[0] < centers[:, 0]) * (rect[1] < centers[:, 1])

                # mask in all gt boxes that under and to the right of centers
                m2 = (rect[2] > centers[:, 0]) * (rect[3] > centers[:, 1])

                # mask in that both m1 and m2 are true
                mask = m1 * m2

                # have any valid boxes? try again if not
                if not mask.any():
                    continue

                # take only matching gt boxes
                current_boxes = boxes[mask, :].copy()

                # take only matching gt labels
                current_labels = labels[mask]

                # should we use the box left and top corner or the crop's
                current_boxes[:, :2] = numpy.maximum(current_boxes[:, :2], rect[:2])
                # adjust to crop (by substracting crop's left,top)
                current_boxes[:, :2] -= rect[:2]

                current_boxes[:, 2:] = numpy.minimum(current_boxes[:, 2:], rect[2:])
                # adjust to crop (by substracting crop's left,top)
                current_boxes[:, 2:] -= rect[:2]

                return current_image, current_boxes, current_labels


class CV2Expand(object):
    def __init__(self, mean: float):
        self.mean = mean

    def __call__(
        self, image: numpy.ndarray, boxes: numpy.ndarray, labels: numpy.ndarray
    ) -> Tuple:
        if random.randint(2):
            return image, boxes, labels

        height, width, depth = image.shape
        ratio = random.uniform(1, 4)
        left = random.uniform(0, width * ratio - width)
        top = random.uniform(0, height * ratio - height)

        expand_image = numpy.zeros(
            (int(height * ratio), int(width * ratio), depth), dtype=image.dtype
        )
        expand_image[..., :] = self.mean
        expand_image[
            int(top) : int(top + height), int(left) : int(left + width)
        ] = image
        image = expand_image

        boxes = boxes.copy()
        boxes[:, :2] += (int(left), int(top))
        boxes[:, 2:] += (int(left), int(top))

        return image, boxes, labels


class CV2RandomMirror(object):
    def __call__(
        self, image: numpy.ndarray, boxes: numpy.ndarray, classes: numpy.ndarray
    ) -> Tuple:
        _, width, _ = image.shape
        if random.randint(2):
            image = image[:, ::-1]
            boxes = boxes.copy()
            boxes[:, 0::2] = width - boxes[:, 2::-2]
        return image, boxes, classes


class CV2SwapChannels(object):
    """Transforms a tensorized image by swapping the channels in the order
specified in the swap tuple.
Args:
swaps (int triple): final order of channels
    eg: (2, 1, 0)
"""

    def __init__(self, swaps: Triple):
        self.swaps = swaps

    def __call__(self, image: numpy.ndarray) -> numpy.ndarray:
        """
Args:
image (Tensor): image tensor to be transformed
Return:
a tensor with channels swapped according to swap
"""
        # if torch.is_tensor(image):
        #     image = image.data.cpu().numpy()
        # else:
        #     image = numpy.array(image)
        image = image[..., self.swaps]
        return image


class CV2PhotometricDistort(object):
    def __init__(self):
        self.pd = [
            CV2RandomContrast(),  # RGB
            CV2ConvertColor(current="RGB", transform="HSV"),  # HSV
            CV2RandomSaturation(),  # HSV
            CV2RandomHue(),  # HSV
            CV2ConvertColor(current="HSV", transform="RGB"),  # RGB
            CV2RandomContrast(),  # RGB
        ]
        self.rand_brightness = CV2RandomBrightness()
        self.rand_light_noise = CV2RandomLightingNoise()

    def __call__(
        self, image: numpy.ndarray, boxes: numpy.ndarray, labels: numpy.ndarray
    ) -> Tuple:
        im = image.copy()
        im, boxes, labels = self.rand_brightness(im, boxes, labels)
        if random.randint(2):
            distort = CV2Compose(self.pd[:-1])
        else:
            distort = CV2Compose(self.pd[1:])
        im, boxes, labels = distort(im, boxes, labels)
        return self.rand_light_noise(im, boxes, labels)
