#!/usr/bin/env /usr/bin/python3
import datetime
import json
import os.path
from pathlib import Path

import upload_youtube
import config
import glob
import time
import subprocess

def get_meta(meta_file):
    with open(meta_file) as fh:
        meta = json.load(fh)
        if not 'done' in meta:
            meta['done'] = []
    return (meta)


def save_meta(meta_file, meta):
    with open(meta_file, 'w') as fh:
        json.dump(meta, fh)


def get_tmp_file(file):
    return(config.tmp_dir+os.path.basename(file))


def get_tag_file(file, tag):
    return (file+"."+tag)

def tag_file(file, tag):
    Path(get_tag_file(file,tag)).touch()

def is_tagged(file, tag):
    return os.path.isfile(get_tag_file(file,tag))

def concat_videos(video_files, output):

    print ("Concatting {} to {}".format(video_files, output))

    if os.path.isfile(output):
        print ("Already concatted")
        return


    list_file_name = config.upload_dir + "files.txt"
    with open(list_file_name, "w") as fh:
        for video_file in video_files:
            fh.write("file '{}'\n".format(video_file))

    subprocess.check_call("ffmpeg -y -f concat -safe 0 -i '{}' -c copy '{}'".format(list_file_name, get_tmp_file(output)), shell=True)
    os.rename(get_tmp_file(output), output)

def do_uploads(video_file, meta):
    print ("Processing uploads for {}".format(video_file))

    youtube_done_file=video_file+".youtube"
    if not is_tagged(video_file, 'youtube'):
        print("Uploading to youtube")
        upload_youtube.upload(
            video_file,
            "My cats eating {}".format(meta['date']),
            "Every time a cat eats it streams automaticly to youtube.\nIts a scale and automated feeder i build to diet my cat. (Mogwai, the black white one)\nThe grey cat is Tracy. :)\n\nMore info: https://github.com/psy0rz/meowton/wiki",
            ["cats", "animal", "eating", "food", "meowton"],
            "animals",
            "en-US",
            "public"
        )
        tag_file(video_file, "youtube")
        print("Done")


print("Scanning " + config.upload_dir)

meta_files = glob.glob(config.upload_dir + "*.meta")
meta_files.sort(key=os.path.getmtime)

prev_day = None
day_files = []

for meta_file in meta_files:
    print("Processing {} ...".format(meta_file))
    base_name = os.path.splitext(meta_file)[0]
    video_file = base_name + ".h264"
    meta = get_meta(meta_file)

    #get record day of file
    mtime=datetime.datetime.fromtimestamp(os.path.getmtime(meta_file))
    day = mtime.strftime("%m-%d-%Y")
    if prev_day == None:
        prev_day = day

    if day != prev_day:
        # upload
        concat_file="{}{}.h264".format(config.upload_dir, prev_day)
        concat_videos(day_files, concat_file)
        do_uploads(concat_file, { "date": prev_day})

        prev_day = day
        day_files = []

    day_files.append(video_file)
