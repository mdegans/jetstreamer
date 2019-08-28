import json
import logging
import time

import jetstreamer

# try to import Jetson Inference and provide instructions to install
# if not available:
try:
    import jetson.inference
    import jetson.utils
except ImportError as e:
    raise ImportError(jetstreamer.ERR_JETSON_NOT_INSTALLED) from e

# Typing:
from typing import (
    Iterable,
    Iterator,
)
from jetstreamer import Frame

logger = logging.getLogger(__name__)

__all__ = {
    "jetson_camera_source",
    "jetson_classifier",
    "jetson_detector",
    "jetson_sequence_sink"
}


def jetson_camera_source(
        width: int = jetstreamer.DEFAULT_CAMERA_RES[0],
        height: int = jetstreamer.DEFAULT_CAMERA_RES[1],
        camera: str = jetstreamer.DEFAULT_CAMERA) -> Iterator[Frame]:
    """
    :yields: jetstreamer.Frame objects from jetson.utils.gstCamera

    :param width: camera width
    :param height: camera height
    :param camera: the camera to use as either a v4l2 path (eg. /dev/video0)
                   or "0" to use the CSI camera.
                   (default: {jetstreamer.DEFAULT_CAMERA})
    """
    # TODO: add frame rate control to capture at consistent intervals
    logger.info(
        f"created {width}x{height} camera source from "
        f"{camera if camera != '0' else 'CSI camera'}")
    frame_counter = 0
    camera = jetson.utils.gstCamera(width, height, camera)
    while True:
        metadata = {
            "fnum": frame_counter,
            "timestamp": time.time()
        }
        frame = metadata, camera.CaptureRGBA(zeroCopy=True)
        frame_counter += 1
        yield frame


def jetson_classifier(source: Iterable[Frame], network, *args
                      ) -> Iterator[Frame]:
    """
    Classifies images from a source Iterable of Frames and
    :yields: jetstreamer.Frame objects with classification metadata attached

    :arg source: an Iterable (list, tuple, generator, etc.) of Frames
    :arg network: the network type to use as string
    :arg *args: additional arguments to pass to jetson.inference.ImageNet
    """
    logger.info(
        f"created jetson_classifier element with '{network}' network")
    classifier = jetson.inference.imageNet(network, *args)
    for frame in source:
        metadata, image = frame
        cid, confidence = classifier.Classify(*image)
        metadata["cid"] = cid
        metadata["confidence"] = confidence
        yield frame  # yields modified metadata as well since a dict is mutable.


def jetson_detector(source: Iterator[Frame], network: str, *args,
                    threshold: float = jetstreamer.DEFAULT_DETECTION_THRESHOLD,
                    ) -> Iterator[Frame]:
    """
    Detects objects from a source Iterable of Frames and
    :yields: jetstreamer.Frame objects with detection metadata attached

    :arg source: an Iterable (list, tuple, generator, etc.) of Frames
    :arg network: the network type to use as string
    :arg *args: additional arguments to pass to detectnet
    :param threshold: detectNet detection threshold as float
    """
    detector = jetson.inference.detectNet(network, args, threshold)
    for frame in source:
        metadata, image = frame
        detections = detector.Detect(*image)
        metadata["detections"] = detections
        yield frame


def jetson_sequence_sink(source: Iterable[Frame],
                         base_filename: str = "",
                         separator: str = "-",
                         extension: str = jetstreamer.DEFAULT_FORMAT) -> None:
    """
    Writes an Iterable of Frame objects to file along with metadata in a
    json lines (jl) sidecar file.

    :arg source: a source Iterable of Frame objects
    :param base_filename: base filename to use
    :param separator: separator to use between elements of the filename
    :param extension: the file format and extension to save the image as
    """
    if not base_filename:
        separator = ""

    meta_filename = f"{base_filename if base_filename else 'metadata'}.jsonl"
    with open(meta_filename, "w") as f:
        for frame in source:
            metadata, image = frame
            fnum = metadata['fnum']
            f.write(json.dumps(metadata) + "\n")
            jetson.utils.saveImageRGBA(
                f"{base_filename}{separator}{fnum}.{extension}",
                *image)
            if fnum % 10 == 0:
                logger.info(f"Wrote {fnum} frames.")
