import jetstreamer

__all__ = [
    "cli_main",
    "main",
]


def cli_main():
    import logging
    import argparse
    import fractions

    class Formatter(argparse.ArgumentDefaultsHelpFormatter,
                    argparse.RawTextHelpFormatter):
        # Multiple formatter classes are not allowed,
        # but they work fine as mixins
        pass

    ap = argparse.ArgumentParser(
        description=
"""Classify, Detect, or simply save frames from camera using Jetson Inference and Jetson Utils. 

Press Ctrl+C or send SIGINT to stop.

examples: 
  jetstreamer --classify googlenet outfilename
  jetstreamer --detect pednet outfilename
  jetstreamer --detect pednet --classify googlenet outfilename""",
        formatter_class=Formatter,
    )

    ap.add_argument("base_filename",
                    help="base filename for images and sidecar files")
    ap.add_argument("--camera", help="v4l2 device (eg. /dev/video0) "
                                     "or '0' for CSI camera",
                    default=jetstreamer.DEFAULT_CAMERA)
    ap.add_argument("--width", type=int, help="camera capture width",
                    default=jetstreamer.DEFAULT_CAMERA_RES[0])
    ap.add_argument("--height", type=int, help="camera capture height",
                    default=jetstreamer.DEFAULT_CAMERA_RES[1])
    ap.add_argument("--interval", type=fractions.Fraction,
                    help="interval between captures in seconds as float, "
                         "fraction, or integer. Default is to capture as fast "
                         "as the gstCamera will allow (currently 30fps) and the"
                         "pipeline can process.")
    ap.add_argument("--classify", help="classification network to use",)
    ap.add_argument("--detect", help="detection network to use",)
    ap.add_argument("--detect-threshold", help="detectNet threshold",
                    default=jetstreamer.DEFAULT_DETECTION_THRESHOLD)
    ap.add_argument("--format",
                    help="format to save image sequence in "
                         "(jpg is probably fastest)",
                    default=jetstreamer.DEFAULT_FORMAT,
                    choices=sorted(jetstreamer.FORMAT_CHOICES),
                    dest="format_")

    # TODO: maybe add debug logging code and argparse argument
    logging.basicConfig(level=logging.INFO)

    args = ap.parse_args()
    main(**vars(args))


def main(base_filename,
         camera=jetstreamer.DEFAULT_CAMERA,
         interval=None,
         width=jetstreamer.DEFAULT_CAMERA_RES[0],
         height=jetstreamer.DEFAULT_CAMERA_RES[1],
         classify=None,
         detect=None,
         detect_threshold=jetstreamer.DEFAULT_DETECTION_THRESHOLD,
         format_=jetstreamer.DEFAULT_FORMAT,):
    # putting it here because jetson.inference.__init__.py prints a ton of stuff
    # on import
    import jetstreamer.pipeline

    # write config to file to load later
    # todo: write code to parse config
    with open(f"{base_filename}.nfo", "w") as nfo_file:
        nfo_file.write(
f"""camera={camera}
interval={interval}
width={width}
height={height}
classify={classify}
detect={detect}
detect_threshold={detect_threshold}
format_={format_}
""")

    # all pipeline functions that follow until the sink are Iterators[Frame]
    # (generators/coroutines that only yield and have no send/return)
    frames = jetstreamer.pipeline.jetson_camera_source(
        width, height, camera, interval)

    # if classification is requested, add it to the pipeline
    if classify:
        frames = jetstreamer.pipeline.jetson_classifier(frames, classify)

    # if detection is requested, add it to the pipeline
    if detect:
        frames = jetstreamer.pipeline.jetson_detector(
            frames, detect, threshold=detect_threshold)

    # the sink that pulls the frames through the pipeline
    try:
        jetstreamer.pipeline.jetson_sequence_sink(frames,
                                                  base_filename=base_filename,
                                                  extension=format_)
    except KeyboardInterrupt:
        print(" Caught interrupt. Quitting.")


if __name__ == '__main__':
    cli_main()
