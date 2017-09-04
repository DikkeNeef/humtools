#!/usr/bin/env python
"""
File name:          server.py
Author:             Dikke Neef
Date created:       28/08/2017
Date last modified: 01/09/2017
Python Version:     2.7.13
"""
# ==============================================================================
from functools import partial
from PIL import Image
import threading
import schedule
import zerorpc
import json
import time

try:
    import cPickle as pickle
except ImportError:
    import pickle

class Slicer(object):
    def __init__(self):
        pass

    def slice(self, seconds, blacklist, d=None):
        if d is not None:
            x = d['x']
            y = d['y']
            w = d['w']
            h = d['h']
            # TODO - slice specific area
        else:
            pass
            # TODO - slice full area


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


def prettify(d):
    return json.dumps(d, indent=4, sort_keys=True)


def stringify(d):
    return json.dumps(d)


def load(path_file):
    return json.load(open(path_file, 'r'))

def loads(d):
    return json.loads(d)


def save_object(obj, fn='zerorpc'):
    print("saving")
    with open(fn + '.db', 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def open_object(fn='zerorpc'):
    return pickle.load(open(fn + '.db', "rb"))


class HumongousTools(object):
    def __init__(self, folder="work/"):
        self.core = folder + "core.json"
        self.scheduler = None
        self.folder = folder

    def total_scenes(self):
        core = load(self.core)
        scenes = len(core)
        return scenes

    def get_animations(self, scene):
        core = load(self.core)
        _scene = core[scene]
        for animation in _scene["animations"]:
            yield {"guid": animation, "name": animation["name"]}

    def get_conversations(self, scene):
        core = load(self.core)
        _scene = core[scene]
        for animation in _scene["animations"]:
            yield {"guid": animation, "name": animation["conv"]}

    def load_object_tree(self):
        d = {}
        for scene in range(self.total_scenes()):
            d[str(scene)] = []
            for animation in self.get_animations(scene):
                d[str(scene)].append(animation)

        return d

    def load_scene_tree(self):
        return {"scenes": self.total_scenes()}

    def load_conversation_tree(self):
        d = {}
        for scene in range(self.total_scenes()):
            d[str(scene)] = []
            for animation in self.get_conversations(scene):
                d[str(scene)].append(animation)

        return d

    def load_object_properties(self, scene, guid):
        core = load(self.core)
        a = core[scene]["animations"][guid]
        return {
            "guid": guid,
            "name": a["name"],
            "sound": a["sound"] if a["sound"] != "" else guid,
            "script": a["script"],
            "stop": a["stop"],
            "params": a["params"],
            "blacklist": a["blacklist"],
            "singleton": a["singleton"],
            "block": a["block"],
            "loop": a["loop"],
            "x": a["x"],
            "y": a["y"],
            "w": a["w"],
            "h": a["h"]
        }

    def load_sound(self, scene, guid):
        core = load(self.core)
        a = core[scene]["animations"][guid]
        return {
            "path_file": [
                '%s%s/%s/animations/%s/%s.mp3' % (
                    self.folder, "scene", str(scene), guid, a["sound"] if a["sound"] != "" else guid
                ),
                '%s%s/%s/animations/%s/%s.ogg' % (
                    self.folder, "scene", str(scene), guid, a["sound"] if a["sound"] != "" else guid
                )
            ]
        }

    def load_background(self, scene):
        return {"path_file": '%s%s/%s/background.png' % (self.folder, "scene", str(scene))}

    def load_music(self, scene):
        return {
            "path_file": [
                '%s%s/%s/music.mp3' % (self.folder, "scene", str(scene)),
                '%s%s/%s/music.ogg' % (self.folder, "scene", str(scene))
            ]
        }

    def backup(self):
        self.scheduler = Scheduler(partial(save_object, self))

    def get_size(self, path_file):
        im = Image.open(path_file)
        return im.size

    def slice(self, post):
        blacklist = {}
        d = loads(post)
        x = d["x"]
        y = d["y"]
        w = d["w"]
        h = d["h"]
        scene = d["scene"]
        seconds = d["seconds"]

        slicer = Slicer()
        for animation in self.get_animations(scene):
            guid = animation["guid"]
            properties = self.load_object_properties(scene, guid)
            if properties["blacklist"]:
                path = self.folder + "tmp/" + str(scene) + '/' + str(guid) + '/slice/'
                for seq in properties['sequence']:
                    for img in seq:
                        filename = img['i']
                        path_file = path + filename
                        w, h = self.get_size(path_file)
                        if not path_file + ':%s,%s' % (img['x'], img['y']) in blacklist:
                            blacklist[path_file + ':%s,%s' % (img['x'], img['y'])] = {
                                'x': img['x'],
                                'y': img['y'],
                                'w': w,
                                'h': h,
                                'i': path_file
                            }

        print(prettify(blacklist))

        if d["blacklist"]:
            slicer.slice(seconds, blacklist, {'x': x, 'y': y, 'w': w, 'h': h})
        else:
            slicer.slice(seconds, blacklist)



def main():
    reload_server = True
    server = HumongousTools()
    if not reload_server:
        server = open_object()

    server.backup()
    s = zerorpc.Server(server)
    s.bind("tcp://0.0.0.0:4242")
    s.run()

if __name__ == '__main__':
    main()
