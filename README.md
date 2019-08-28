# JetStreamer
JetStreamer is a command line utility* to record frames and perform inferences 
from a camera on NVIDIA Tegra. It uses the Jetson Inference library which is
comprised of utilities and wrappers around lower level NVIDIA inference 
libraries.

*display support is planned

## Requirements
The only requirement for installation is the
[Jetson Inference repository](https://github.com/dusty-nv/jetson-inference.git).

To build and install Jetson Inference on your Tegra device, run these commands
on the device itself or via ssh:

```shell
sudo apt install git cmake python3-dev
cd ~
git clone https://github.com/dusty-nv/jetson-inference.git
cd jetson-inference
git submodule update --init
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX=~/.local ..
make -j4 && sudo make install
```

**warning: do not delete the jetson-inference folder** since there is a 
symlink from /usr/local/bin/networks to jetson-inference/data/networks
 
**Optional fix for above warning if you're the paranoid/perfectionist type**:

Instead it's recommended to run the app with the networks you want *first* to 
generate the optimized networks, *then* copy them over, and *then* delete the 
build folder. After you've the run the app as your build user and see something
like this for **each of the networks you need**...
```
[TRT]   device GPU, completed writing engine cache to /usr/local/bin/networks/ped-100/snapshot_iter_70800.caffemodel.1.1.GPU.FP16.engine
```
...perform the following steps to copy the files over as root so that they're
both immutable to and accessable to all users (eg, a system user running 
jetstreamer as a daemon)
```
sudo rm /usr/local/bin/networks
sudo cp -r ~/jetson-inference/data/networks /usr/local/bin
rm -rf ~/jetson-inference
```

## installation
(on your tegra device)
```shell
pip3 install jetstreamer
```

**Warning**: don't **ever** run pip with sudo. If an app requests you do this,
uninstall it **immediately**, even if you're not the paranoid type.

Pypi if **full** of malware (docker hub and npm are worse) and even a well 
intentioned author might include a malicious package. Installing it or running 
it as your root user could compromise your Tegra device, potentially leading to 
a compromise of your entire network.

## Usage
Simply run `jetstreamer` after installation.

```
$ jetstreamer --help
usage: __main__.py [-h] [--camera CAMERA] [--width WIDTH] [--height HEIGHT]
                   [--classify CLASSIFY] [--detect DETECT]
                   [--detect-threshold DETECT_THRESHOLD] [--format {jpg,png}]
                   base_filename

Classify, Detect, or simply save frames from camera using Jetson Inference and Jetson Utils. 

Press Ctrl+C or send SIGINT to stop.

examples: 
  jetstreamer --classify googlenet outfilename
  jetstreamer --detect pednet outfilename
  jetstreamer --detect pednet --classify googlenet outfilename

positional arguments:
  base_filename         base filename for images and sidecar files

optional arguments:
  -h, --help            show this help message and exit
  --camera CAMERA       v4l2 device (eg. /dev/video0) or '0' for CSI camera (default: 0)
  --width WIDTH         camera capture width (default: 720)
  --height HEIGHT       camera capture height (default: 480)
  --classify CLASSIFY   classification network to use (default: None)
  --detect DETECT       detection network to use (default: None)
  --detect-threshold DETECT_THRESHOLD
                        detectNet threshold (default: 0.5)
  --format {jpg,png}    format to save image sequence in (jpg is fastest) (default: jpg)
```

## Uninstallation
```shell
pip3 uninstall jetstreamer
```

## FAQ
- **What is the .nfo file for**? The nfo file stores the parameters used to 
launch main() so you know what network, for example, is associated with a given
capture sequence. This lets you look up the description for class ids without
having to store long string and in future versions will allow loading from it
so cid -> class description associations can be made automatically.

- **what is the .jsonl file for** The .jsonl file is a 
[json lines file format](http://jsonlines.org/).
Each line is json containing the frame number and any assocaited metadata.

## Use as a library:
This is not recommended as the API will likely change, but docstrings are
included for every function and pipeline element with the exception of main()
for which one may refer to the above usage.

- **How do I split the pipeline?**
[itertools.tee](https://docs.python.org/3/library/itertools.html#itertools.tee)
will likely do the job. Display sink support is planned using this. Really, 
itertools is the python module you want when dealing with iterators/generators.

- **How do I write my own sink**
You need something that consumes from a generator/iterator. Looping over it or
calling next(source), where source is your generator, will pull frames through
the pipeline.

- **Is a file source planned**
Yes. You will be able to feed it an Iterable of filenames. Also planned is a
source generator with a send method so you push filenames into the source on
demand.

- **Are copies of the data being made as it's passed down the pipeline and into
C functions?**
No. The image is passed back and forth through C in a PyCapsule container which
actually contains a pointer to the image in shared CPU/GPU memory and not the 
image itself. No copies are made.

- **Will you add support for network streaming**? Possibly, if there is enough 
interest.