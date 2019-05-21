#
#  合拼多个小片段
#


import glob
import os
import subprocess
import command
import argparse


def get_sort_key(p, format):
    def sort_key(s):
        print(p, format, s)
        s = s.replace(p, "").replace(".{}".format(format), "")
        return int(s)

    return sort_key


if __name__ == "__main__":
    temp_file = "video.txt"
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str,
                        help='path of video common prefix eg . \'./a/cut_1.mp4.\'\'./a/cut_2.mp4\''
                             ' the common prefix is \'./a/cut_ \' (default: .\\output\\cut_)',
                        default=".\\output\\cut_")
    parser.add_argument('-o', '--output', type=str,
                        help='path of output video (default: result.mp4)', default="result.mp4")
    parser.add_argument('-f', '--format', type=str, help='the format of videos(default:mp4)', default="mp4")
    args = parser.parse_args()

    video_path = args.path + "*.{}".format(args.format)
    print("# video path:", video_path)
    video_list = glob.glob(video_path)
    video_list = sorted(video_list, key=get_sort_key(args.path, args.format))
    temp = open(temp_file, "w")
    for video_name in video_list:
        temp.write("file \'{}\'\n".format(video_name))
    temp.close()
    cmd = command.video_merge.format("video.txt", args.output)
    print("# cmd:", cmd)
    process = subprocess.Popen(cmd)
    process.wait()
    os.remove(temp_file)
    print("# done.")
