#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 20/03/2020
           """

import torch

from draugr.torch_utilities import global_torch_device

__all__ = ["TorchCacheSession"]

from draugr.torch_utilities.sessions.device_sessions import (
    TorchCpuSession,
    TorchCudaSession,
)

from draugr.torch_utilities.sessions.model_sessions import (
    TorchEvalSession,
    TorchTrainSession,
)

from warg.decorators.kw_passing import AlsoDecorator


class TorchCacheSession(AlsoDecorator):
    """
# speed up evaluating after training finished
# NOTE: HAS THE SIDE EFFECT OF CLEARING CACHE, NON RECOVERABLE

"""

    def __init__(self, using_cuda: bool = global_torch_device().type == "cuda"):
        self.using_cuda = using_cuda

    def __enter__(self):
        if self.using_cuda:
            torch.cuda.empty_cache()
        return True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.using_cuda:
            torch.cuda.empty_cache()


if __name__ == "__main__":

    def a():
        print(torch.cuda.memory_cached(global_torch_device()))
        with TorchCacheSession():
            torch.tensor([0.0], device=global_torch_device())
            print(torch.cuda.memory_cached(global_torch_device()))
        print(torch.cuda.memory_cached(global_torch_device()))

    def b():
        model = torch.nn.Sequential(torch.nn.Linear(1, 1), torch.nn.Dropout(0.1))
        print(model.training)
        with TorchEvalSession(model):
            print(model.training)
        print(model.training)

    def c():
        model = torch.nn.Sequential(torch.nn.Linear(1, 1), torch.nn.Dropout(0.1))
        model.eval()
        print(model.training)
        with TorchTrainSession(model):
            print(model.training)
        print(model.training)

    def d():
        print(
            global_torch_device(override=global_torch_device(cuda_if_available=False))
        )
        print(global_torch_device())
        with TorchCudaSession():
            print(global_torch_device())
        print(global_torch_device())

    def e():
        print(global_torch_device(override=global_torch_device(cuda_if_available=True)))
        print(global_torch_device())
        with TorchCpuSession():
            print(global_torch_device())
        print(global_torch_device())

    # a()
    # b()
    # c()
    d()
    e()
