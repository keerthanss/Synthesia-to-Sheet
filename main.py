import argparse
import os
import sys

import synthesia_to_sheet

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("video_file",default="", help="Provide the path to the local synthesia video for processing" )
    args = parser.parse_args()

    if not os.path.exists(args.video_file):
        print "The path provided does not exist. Please check and try again."
        sys.exit(1)

    return args

def run():
    args = get_args()
    list_of_frames = synthesia_to_sheet.parse_video.get_frames()
    # do further processing

if __name__ == '__main__':
    run()
