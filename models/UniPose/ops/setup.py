# ------------------------------------------------------------------------------------------------
# Deformable DETR
# Copyright (c) 2020 SenseTime. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 [see LICENSE for details]
# ------------------------------------------------------------------------------------------------
# Modified from https://github.com/chengdazhi/Deformable-Convolution-V2-PyTorch/tree/pytorch_1.0.0
# ------------------------------------------------------------------------------------------------

import os
import glob

import torch

from torch.utils.cpp_extension import CUDA_HOME
from torch.utils.cpp_extension import CppExtension
from torch.utils.cpp_extension import CUDAExtension

from setuptools import find_packages
from setuptools import setup

requirements = ["torch", "torchvision"]


if os.name == "nt" and os.environ.get("VSCMD_VER"):
    os.environ.setdefault("DISTUTILS_USE_SDK", "1")


def get_extensions():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    extensions_dir = os.path.join(this_dir, "src")

    main_file = glob.glob(os.path.join(extensions_dir, "*.cpp"))
    source_cpu = glob.glob(os.path.join(extensions_dir, "cpu", "*.cpp"))
    source_cuda = glob.glob(os.path.join(extensions_dir, "cuda", "*.cu"))

    sources = main_file + source_cpu
    extension = CppExtension
    extra_compile_args = {"cxx": []}
    define_macros = []

    # import ipdb; ipdb.set_trace()

    if torch.cuda.is_available() and CUDA_HOME is not None:
        nvcc = os.path.join(CUDA_HOME, "bin", "nvcc.exe" if os.name == "nt" else "nvcc")
        if not os.path.isfile(nvcc):
            raise RuntimeError(
                "CUDA_HOME is set to {!r}, but nvcc was not found at {!r}. "
                "Install the NVIDIA CUDA Toolkit that matches your PyTorch CUDA "
                "version, or point CUDA_HOME/CUDA_PATH at that Toolkit root.".format(CUDA_HOME, nvcc)
            )
        extension = CUDAExtension
        sources += source_cuda
        define_macros += [("WITH_CUDA", None)]
        extra_compile_args["nvcc"] = [
            "-DCUDA_HAS_FP16=1",
            "-D__CUDA_NO_HALF_OPERATORS__",
            "-D__CUDA_NO_HALF_CONVERSIONS__",
            "-D__CUDA_NO_HALF2_OPERATORS__",
        ]
        if os.name == "nt":
            extra_compile_args["nvcc"].append("-allow-unsupported-compiler")
            winsdk_bin = os.environ.get("XPOSE_WINSDK_BIN")
            if winsdk_bin:
                os.environ["PATH"] = winsdk_bin + os.pathsep + os.environ.get("PATH", "")
                os.environ["Path"] = winsdk_bin + os.pathsep + os.environ.get("Path", "")
            ccbin = os.environ.get("XPOSE_CCBIN")
            if ccbin:
                ccbin_dir = os.path.dirname(ccbin)
                os.environ["PATH"] = ccbin_dir + os.pathsep + os.environ.get("PATH", "")
                os.environ["Path"] = ccbin_dir + os.pathsep + os.environ.get("Path", "")
                extra_compile_args["nvcc"] += ["-ccbin", ccbin]
            else:
                vc_tools = os.environ.get("VCToolsInstallDir")
                if vc_tools:
                    ccbin_dir = os.path.join(vc_tools, "bin", "Hostx64", "x64")
                    os.environ["PATH"] = ccbin_dir + os.pathsep + os.environ.get("PATH", "")
                    os.environ["Path"] = ccbin_dir + os.pathsep + os.environ.get("Path", "")
                    extra_compile_args["nvcc"] += [
                        "-ccbin",
                        os.path.join(ccbin_dir, "cl.exe"),
                    ]
    else:
        raise NotImplementedError("CUDA is not available")

    sources = [os.path.join(extensions_dir, s) for s in sources]
    include_dirs = [extensions_dir]
    ext_modules = [
        extension(
            "MultiScaleDeformableAttention",
            sources,
            include_dirs=include_dirs,
            define_macros=define_macros,
            extra_compile_args=extra_compile_args,
        )
    ]
    return ext_modules

setup(
    name="MultiScaleDeformableAttention",
    version="1.0",
    author="Weijie Su",
    url="https://github.com/fundamentalvision/Deformable-DETR",
    description="PyTorch Wrapper for CUDA Functions of Multi-Scale Deformable Attention",
    packages=find_packages(exclude=("configs", "tests",)),
    ext_modules=get_extensions(),
    cmdclass={"build_ext": torch.utils.cpp_extension.BuildExtension.with_options(use_ninja=False)},
)
