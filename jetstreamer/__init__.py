from typing import Tuple, MutableMapping

Image = Tuple[object, int, int]
Image.__doc__ = """
A base class for typing representing a Tuple[PyCapsule, int, int]
Where:
    PyCapsule contains a pointer to an image array
    and the ints are width and height, respectively
"""
# (where object is a PyCapsule containing a pointer to an image and the ints are
# width and height, respectively)
Frame = Tuple[MutableMapping, Image]
Frame.__doc__ = """
A base class for typing representing a Tuple[MutableMapping, Image]
Where:
    MutableMapping (eg. dict) contains metadata to be dumped and
    Image is a jetstreamer.Image
"""

DEFAULT_CAMERA_RES = (720, 480)
DEFAULT_CAMERA = "0"
DEFAULT_DETECTION_THRESHOLD = 0.5
# TODO: look at source to figure out all format choices
FORMAT_CHOICES = {"jpg", "png"}
DEFAULT_FORMAT = "jpg"
if DEFAULT_FORMAT not in FORMAT_CHOICES:
    raise KeyError(
        "DEFAULT_FORMAT not in FORMAT_CHOICES (programmer screwed up)")

ERR_JETSON_NOT_INSTALLED = """
Jetson Inference does not appear to be installed.
To install it on your Tegra, run these commands *on your Tegra*:

sudo apt install git cmake python3-dev
cd ~
git clone https://github.com/dusty-nv/jetson-inference.git
cd jetson-inference
git submodule update --init
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX=~/.local ..
make -j4 && sudo make install
"""
