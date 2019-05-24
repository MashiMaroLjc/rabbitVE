video_cut = "ffmpeg -ss {} -to {} -i {} -codec copy -avoid_negative_ts 1 -y {}"
# 参数依次为:开始时间、结束时间、输入视频文件名、输出视频文件名

video_merge="ffmpeg -f concat -safe 0 -i {} -c copy -y {}"
# 参数依次为:要拼接的文件的txt,输出视频文件名字

video_audio_combine = "ffmpeg -i {} -i {} -vcodec copy -acodec copy  -y {}"
# 参数依次为:视频,音频，输出

extract_audio = "ffmpeg  -i {}  -vn -y {}"
# 参数依次为:视频,音频音频

imgs2video = "ffmpeg -i {} -c:v libx264 -vf \"fps={},format=yuv420p\" -y {}"
# 参数依次为:图片匹配字符 fps 输出