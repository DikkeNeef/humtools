#!/usr/bin/env python
"""
File name:          server.py
Author:             Dikke Neef
Date created:       28/08/2017
Date last modified: 04/09/2017
Python Version:     2.7.13
"""
# ==============================================================================
from functools import partial
from utils import *
import zerorpc
import autoit
import uuid
import os


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

    def load_conversation(self, scene, guid):
        core = load(self.core)
        return core[scene]["animations"][guid]["conv"]

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

    def slice(self, post):
        blacklist = {}
        d = loads(post)
        x = d["x"]
        y = d["y"]
        w = d["w"]
        h = d["h"]
        scene = d["scene"]
        seconds = d["seconds"]

        for animation in self.get_animations(scene):
            guid = animation["guid"]
            properties = self.load_object_properties(scene, guid)
            if properties["blacklist"]:
                path = self.folder + "tmp/" + str(scene) + '/' + str(guid) + '/slice/'
                for seq in properties['sequence']:
                    for img in seq:
                        filename = img['i']
                        path_file = path + filename
                        w, h = get_size(path_file)
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
            slice_frames(seconds, blacklist, {'x': x, 'y': y, 'w': w, 'h': h})
        else:
            slice_frames(seconds, blacklist)

    def save_object(self, a, scene, guid):
        core = load(self.core)
        save(self.folder + 'backup/' + uuid.uuid4() + '.json', core)

        d = {
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
            "h": a["h"],
            "conv": {"dutch": [], "english": [], "french": [], "time": []},
            "sequence": a["sequence"]
        }

        core[int(scene)]["animations"][guid] = d
        save(self.core, core)
        return self.load_object_tree()

    def save_conversations(self, conv, scene, guid):
        core = load(self.core)
        save(self.folder + 'backup/' + uuid.uuid4() + '.json', core)
        core[int(scene)]["animations"][guid]["conv"] = conv
        save(self.core, core)
        return self.load_conversation(scene, guid)

    def add_scene(self):
        core = load(self.core)
        save(self.folder + 'backup/' + uuid.uuid4() + '.json', core)

        new_folder = self.folder + 'scene/%s/animations' % (self.total_scenes())
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)

        new_folder = self.folder + 'tmp/%s/animations' % (self.total_scenes())
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)

        d = {
            "container": {},
            "mapper": {}
        }

        core.append(d)
        save(self.core, core)
        return self.load_scene_tree()

    def record_audio_animation(self, scene, guid, seconds=10):
        path_file = "%s%s/%s/%s/%s" % (self.folder, "tmp", str(scene), guid, guid)
        record(path_file, seconds)

    def record_audio_scene(self, scene, seconds=10):
        path_file = "%s%s/%s/music-%s" % (self.folder, "tmp", str(scene), uuid.uuid4())
        record(path_file, seconds)

    def capture_background(self, scene, name="pajama sam", w=640, h=480, ox=8, oy=6):
        path_file = "%s%s/%s/background+%s" % (self.folder, "tmp", str(scene), uuid.uuid4())
        x, y, _, _ = autoit.win_get_pos(name)
        box = screenshot(x+ox, y+oy, w, h)
        png(path_file, box)


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
