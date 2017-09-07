import pyscreenshot
import numpy as np
import threading
import schedule
import pyaudio
import autoit
import wave
import json
import time
import cv2
from PIL import Image
from numpngw import write_png
from pydub import AudioSegment
from ctypes import windll, Structure, c_long, byref

try:
    import cPickle as pickle
except ImportError:
    import pickle


class Scheduler(object):
    def __init__(self, fnc, interval=2):
        self.fnc = fnc
        self.interval = interval
        thread = threading.Thread(target=self.run)
        thread.daemon = False
        thread.start()

    def run(self):
        schedule.every(self.interval).seconds.do(self.fnc)
        while True:
            schedule.run_pending()
            time.sleep(1)


def slice_frames(seconds, blacklist, d=None):
    if d is not None:
        x = d['x']
        y = d['y']
        w = d['w']
        h = d['h']
        # TODO - slice specific area
    else:
        pass
        # TODO - slice full area


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


def get_mouse_position():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return {"x": pt.x, "y": pt.y}


def click(x, y):
    windll.user32.SetCursorPos(x, y)
    windll.user32.mouse_event(2, 0, 0, 0, 0)
    windll.user32.mouse_event(4, 0, 0, 0, 0)


def activate_window(name):
    if autoit.win_exists(name):
        autoit.win_activate(name)

    return autoit.win_wait_active(name, 5)


def screenshot(x=0, y=0, w=640, h=480):
    return np.asarray(pyscreenshot.grab(bbox=(x, y, x+w, y+h)))


def png(filename, array, ext='.png'):
    write_png(str(filename) + ext, array)


def read_image(path):
    if not path.endswith('.png'):
        return np.asarray([])

    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    try:
        b_channel, g_channel, r_channel, a_channel = cv2.split(image)
    except ValueError:
        b_channel, g_channel, r_channel = cv2.split(image)

    alpha_channel = np.full(b_channel.shape, 255, dtype=np.uint8)
    image = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))

    abgr = np.asarray(image)[:, :, ::-1]
    rgb = [abgr[:, :, i] for i in range(1, 4)]
    rgb.append((abgr[:, :, 0]))
    rgba = np.dstack(tuple(rgb))

    return rgba


def get_size(path_file):
    im = Image.open(path_file)
    return im.size


def prettify(d):
    return json.dumps(d, indent=4, sort_keys=True)


def stringify(d):
    return json.dumps(d)


def load(path_file):
    return json.load(open(path_file, 'r'))


def save(path_file, d):
    with open(path_file, 'w') as f:
        json.dump(d, f, indent=4, sort_keys=True)


def loads(d):
    return json.loads(d)


def save_object(obj, fn='zerorpc'):
    with open(fn + '.db', 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def open_object(fn='zerorpc'):
    return pickle.load(open(fn + '.db', "rb"))


def record(path_file, seconds=10):
    default_frames = 44100
    recorded_frames = []

    p = pyaudio.PyAudio()

    try:
        default_device_index = p.get_default_input_device_info()
    except IOError:
        default_device_index = -1

    for i in range(0, p.get_device_count()):
        info = p.get_device_info_by_index(i)

        if default_device_index == -1:
            default_device_index = info["index"]

    if default_device_index == -1:
        return True

    try:
        device_info = p.get_device_info_by_index(0)
    except TypeError:
        device_info = p.get_device_info_by_index(default_device_index)

    channel_count = (device_info["maxInputChannels"] if
                    (device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else
                    device_info["maxOutputChannels"])

    print(device_info["defaultSampleRate"])
    stream = p.open(format=pyaudio.paInt16,
                    channels=channel_count,
                    rate=int(device_info["defaultSampleRate"]),
                    input=True,
                    frames_per_buffer=default_frames,
                    input_device_index=device_info["index"],
                    as_loopback=True)

    for i in range(0, int(int(device_info["defaultSampleRate"]) / default_frames * seconds)):
        recorded_frames.append(stream.read(default_frames))

    stream.stop_stream()
    stream.close()
    p.terminate()

    wave_file = wave.open(path_file + '.wav', 'wb')
    wave_file.setnchannels(channel_count)
    wave_file.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wave_file.setframerate(int(device_info["defaultSampleRate"]))
    wave_file.writeframes(b''.join(recorded_frames))
    wave_file.close()

    AudioSegment.from_wav(path_file + '.wav').export(path_file + '.mp3', format="mp3")
    AudioSegment.from_wav(path_file + '.wav').export(path_file + '.ogg', format="ogg")
