import argparse
import os

import signal

import pickle

from Arducam import *
from ImageConvert import *

exit_ = False


def sigint_handler(signum, frame):
    global exit_
    exit_ = True


signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGTERM, sigint_handler)


def display_fps(index):
    display_fps.frame_count += 1

    current = time.time()
    if current - display_fps.start >= 1:
        print("fps: {}".format(display_fps.frame_count))
        display_fps.frame_count = 0
        display_fps.start = current


display_fps.start = time.time()
display_fps.frame_count = 0


def white_balance_loops(img):
    result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 2.5)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 2.5)
    result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return result


if __name__ == "__main__":
    time_start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--config-file', type=str, required=True, help='Specifies the configuration file.')
    parser.add_argument('-v', '--verbose', action='store_true', required=False, help='Output device information.')
    parser.add_argument('--preview-width', type=int, required=False, default=-1, help='Set the display width')
    parser.add_argument('-n', '--nopreview', action='store_true', required=False, help='Disable preview windows.')
    parser.add_argument('-play', '--play', action='store_true', default=False, required=False, help='Preview the video')

    args = parser.parse_args()
    config_file = args.config_file
    verbose = args.verbose
    preview_width = args.preview_width
    no_preview = args.nopreview
    play = args.play

    camera = ArducamCamera()

    if not camera.openCamera(config_file):
        raise RuntimeError("Failed to open camera.")

    if verbose:
        camera.dumpDeviceInfo()

    camera.start()
    # camera.setCtrl("setFramerate", 2)
    # camera.setCtrl("setExposureTime", 20000)
    # camera.setCtrl("setAnalogueGain", 800)
    scale_width = preview_width

    cwd = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir(os.path.join(cwd, 'output')):
        os.makedirs(os.path.join(cwd, 'output'))
    os.chdir(os.path.join(cwd, 'output'))
    while not exit_:
        ret, data, cfg = camera.read()

        display_fps(0)
        if no_preview:
            continue

        if ret:
            image = white_balance_loops(convert_image(data, cfg, camera.color_mode))

            if play:
                if scale_width != -1:
                    scale = scale_width / image.shape[1]
                    image = cv2.resize(image, None, fx=scale, fy=scale)
                cv2.imshow("Arducam", image)
            else:

                cv2.imwrite('Finalcolortest1.png', image)
                exit_ = True

        else:
            print("timeout")

        key = cv2.waitKey(1)
        if key == ord('q'):
            exit_ = True
        elif key == ord('s'):
            np.array(data, dtype=np.uint8).tofile("image.raw")

    camera.stop()
    camera.closeCamera()
    time_end = time.time()

    print('elapsed', time_end - time_start)

