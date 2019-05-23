# rabbitVE
[![Badge](https://img.shields.io/badge/link-996.icu-%23FF4D5B.svg?style=flat-square)](https://996.icu/#/en_US)
=======



English Description:

> RabbitVE ,rabbit video edit, which is a open video edit software using AI.
>
> For now ,rabbitVE support video clip for special person to make a personal video clip,which usually  be an  importance part of fans activities  in China.
>
> There is a demo about ChaoYue Yang,who is a idol of China. From *`Super Start Games`*, a two-hour TV program,rabbitVE cut a 16 minute fragment of ChaoYue Yang.
>
> You can see the demo in  this link. [bilibili](https://www.bilibili.com/video/av53132715) 
>
> In the future,I intent to add some new feature for the software.For example, ban the person ,who you don't want to see ,in the video , like [this](https://github.com/minimaxir/person-blocker) ,clean this  people using Image-Inpainting like [this](https://github.com/MathiasGruber/PConv-Keras),or some image translation based GAN.
>
> But there is still a long way to go.
>
> Thank for you watching and  giving me a start.



----

## 中文版

rabbitVE是一个意图使用AI技术进行视频编辑的软件，目前还在初级阶段。在参考[这篇知乎文章](https://zhuanlan.zhihu.com/p/66248591)后获得的灵感，因此第一个实现的技术也是基于face location 和face recognition以及一系列修正算法做出的视频单人剪辑。但很遗憾的一点是，虽然在原作者的实现上做出了一点改进，但仍然没法做到全自动，虽然一定的人工干预。

Demo：

视频： [bilibili](https://www.bilibili.com/video/av53132715)  《超新星全运会》 2018.11.11期 杨超越单人cut

原视频：《超新星全运会》 2018.11.11期

## 项目依赖

- python 3.6+
- opencv 3.3+
- dlib
- scipy
- ffmpeg
- moviepy

### 文件介绍

- tool_clip.py 从视频上直接剪辑与face database相关人物的帧。
- tool_extract.py 可以从视频或图片集上剪裁人脸，并输出在指定的目录里（face database）
- tool_sort.py 对剪裁出来的人脸根据某一相似度量方法排序并输出，方便用于在剪裁后的人脸进行人工去重或剔除无关样本。
- tool_merge.py 对从视频上剪辑出来的片段按顺序合成。

目前不同功能以单个脚本的形式存在，迟点会整合和各功能插件化，至于GUI会视项目发展情况来决定是否添加。

### 未来

首先一点，对于更好，更快的人脸模型是刚需，会定期考虑整合前沿相关技术。

其次一点是会考虑引入一个逐帧进行处理的技术，这样可以配合相关的语义分割/实例分割技术，进行对指定的样本的[智能打码](https://github.com/minimaxir/person-blocker)，使用图像补全的技术进行[智能清除该对象](https://github.com/MathiasGruber/PConv-Keras)，或这使用各种基于GAN的技术等。

总而言之，能搞的东西很多，欢迎关注和PR。

### Lincense

GPL 3.0
