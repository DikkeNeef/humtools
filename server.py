#!/usr/bin/env python
"""
File name:          server.py
Author:             Dikke Neef
Date created:       28/08/2017
Date last modified: 07/09/2017
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

    def get_conversation(self, d):
        guid = d["guid"]
        scene = d["scene"]
        core = load(self.core)
        _scene = core[int(scene)]
        return stringify(_scene["animations"][guid]["conv"])

    def get_animations(self, scene):
        core = load(self.core)
        _scene = core[int(scene)]
        for animation in _scene["animations"]:
            yield {"guid": animation, "name": animation["name"]}

    def get_conversations(self, scene):
        core = load(self.core)
        _scene = core[int(scene)]
        for animation in _scene["animations"]:
            print(animation)
            yield {"guid": animation,
                   "name": _scene["animations"][animation]["name"],
                   "conv":_scene["animations"][animation]["conv"]}

    def load_object_tree(self):
        d = {}
        for scene in range(self.total_scenes()):
            d[str(scene)] = []
            for animation in self.get_animations(scene):
                d[str(scene)].append(animation)

        return d

    def load_scene_tree(self):
        print(stringify({"scenes": self.total_scenes()}))
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

    def load_object_properties(self, d):
        core = load(self.core)
        scene, guid = d["scene"], d["guid"]
        a = core[scene]["animations"][guid]
        return a

    def load_sound(self, scene, guid):
        core = load(self.core)
        a = core[scene]["animations"][guid]
        return {
            "path_file":
                '%s%s/%s/animations/%s/%s' % (
                    self.folder, "scene", str(scene), guid, a["sound"] if a["sound"] != "" else guid
                )
        }

    def load_background(self, d):
        return stringify({
            "path_file": '%s%s/%s/background.png' % (self.folder, "scene", str(d['scene']))
        })

    def load_music(self, d):
        return stringify({
            "path_file": "%s%s/%s/music" % (self.folder, "scene", str(d['scene']))
        })

    def backup(self):
        self.scheduler = Scheduler(partial(save_object, self))

    def _slice(self, post):
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
            properties = self.load_object_properties({"scene": scene, "guid": guid})
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

        return({"status": "Slicing has started, please wait", "time": seconds})

    def save_object(self, d):
        core = load(self.core)
        save(self.folder + 'backup/' + str(uuid.uuid4()) + '.json', core)
        core[int(d["scene"])]["animations"][d["guid"]] = d["a"]
        save(self.core, core)
        return self.load_object_tree()

    def save_conversations(self, d):
        conv = d["conv"]
        guid = d["guid"]
        scene = d["scene"]
        core = load(self.core)
        save(self.folder + 'backup/' + str(uuid.uuid4()) + '.json', core)
        core[int(scene)]["animations"][guid]["conv"] = conv
        save(self.core, core)
        return stringify(self.load_conversation(scene, guid))

    def add_scene(self):
        core = load(self.core)
        save(self.folder + 'backup/' + str(uuid.uuid4()) + '.json', core)

        new_folder = self.folder + 'scene/%s/animations' % (self.total_scenes())
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)

        new_folder = self.folder + 'tmp/%s/animations' % (self.total_scenes())
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)

        d = {
            "animations": {},
            "mapper": {}
        }

        core.append(d)
        save(self.core, core)
        return self.load_scene_tree()

    def record_audio_animation(self, scene, guid, seconds=10):
        path_file = "%s%s/%s/%s/%s" % (self.folder, "tmp", str(scene), guid, guid)
        record(path_file, seconds)
        return {"status": "recording animation, please wait until done", "wait": seconds}

    def record_audio_scene(self, d, seconds=10, name="Untitled - Paint"):
        activate_window(name)
        tpath_file = "%s%s/%s/music-%s" % (self.folder, "tmp", str(d["scene"]), uuid.uuid4())
        spath_file = "%s%s/%s/music" % (self.folder, "scene", str(d["scene"]))
        path_files = [tpath_file, spath_file]
        record(path_files, seconds)
        return stringify({"status": "recording background, please wait until done", "wait": seconds})

    def capture_background(self, d, w=640, h=480, ox=9, oy=24, name="Untitled - Paint"):
        activate_window(name)
        print(d)
        tpath_file = "%s%s/%s/background-%s" % (self.folder, "tmp", str(d["scene"]), uuid.uuid4())
        spath_file = "%s%s/%s/background" % (self.folder, "scene", str(d["scene"]))
        x, y, _, _ = autoit.win_get_pos(name)
        box = screenshot(x+ox, y+oy, w, h)
        png(tpath_file, box)
        png(spath_file, box)
        return stringify({"status": "background captured"})


def main():
    server = HumongousTools()
    server.backup()
    s = zerorpc.Server(server)
    s.bind("tcp://0.0.0.0:4242")
    s.run()

if __name__ == '__main__':
    main()
