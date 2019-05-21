video_cut = "ffmpeg -ss {} -to {} -i {} -codec copy -avoid_negative_ts 1 -y {}"
# 参数依次为:开始时间、结束时间、输入视频文件名、输出视频文件名

video_merge="ffmpeg -f concat -safe 0 -i {} -c copy -y {}"
# 参数依次为:要拼接的文件的txt,输出视频文件名字