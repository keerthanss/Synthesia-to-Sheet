from __future__ import unicode_literals

import argparse
import os
import sys
import youtube_dl

from synthesia_to_sheet import *

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_file",default="", help="Provide the path to the local synthesia video for processing" )
    parser.add_argument("--url", default="",  help="Provide the url to download the youtube video")
    args = parser.parse_args()

    if not args.video_file and not args.url:
        print "Please provide at least one source for video - local file or URL"
        sys.exit(1)

    if args.video_file and args.url:
        print "Multiple inputs provided! Please select exactly one source for video - either local file or a URL"
        sys.exit(1)
    elif args.video_file:
        if not os.path.exists(args.video_file):
            print "The path to local video file does not exist. Please check and try again."
            sys.exit(1)

    return args

def download_video(url):
    DOWNLOADED_FILENAME = "out.mp4"
    ydl_opts = {
        "format" : "[height<=360][ext=mp4]",  # mandate a mp4 video whose resolution is maximum 360p
        "quiet" : False,
        "outtmpl" : DOWNLOADED_FILENAME
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return DOWNLOADED_FILENAME

def run():
    args = get_args()
    if args.url:
        try:
            args.video_file = download_video(args.url)
        except Exception as e:
            print e
            sys.exit(1)
        else:
            print "Video successfully downloaded"
    list_of_frames = parse_video.get_frames(args.video_file)
    parse_video.display_frames(list_of_frames)
    # do further processing

if __name__ == '__main__':
    run()
