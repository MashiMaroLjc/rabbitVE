from .BasePlugin import BasePlugin
from .param_type import *
import cv2


class Cartoonlization(BasePlugin):
    def __init__(self):
        super(Cartoonlization, self).__init__()

    def initialize(self, params):
        self.num_down = params["Num_Down"]
        self.num_bilateral = params["Num_Bilateral"]
        self.mbk = params["Median_Blur_Kernel"]
        self.D = params["Bilateral_Filter_Kernel_Size"]
        self.Sigma_Coloe = params["Sigma_Coloe"]
        self.Sigma_Space = params["Sigma_Space"]
        self.Save_Edge = params["Save_Edge"]
        self.Adaptive_Threshold_Block_Size = params["Adaptive_Threshold_Block_Size"]
        self.C = params["C"]

    def render_info(self):

        need2render = list()
        need2render.append({
            "name": "Num_Down",
            "type": INT,
            "default": 2,
        })
        need2render.append({
            "name": "Num_Bilateral",
            "type": INT,
            "default": 7,
        })
        need2render.append({
            "name": "Median_Blur_Kernel",
            "type": INT,
            "default": 7,
        })
        need2render.append({
            "name": "Bilateral_Filter_Kernel_Size",
            "type": INT,
            "default": 9,
        })
        need2render.append({
            "name": "Sigma_Coloe",
            "type": INT,
            "default": 9,
        })
        need2render.append({
            "name": "Sigma_Space",
            "type": INT,
            "default": 7,
        })
        need2render.append({
            "name": "Save_Edge",
            "type": BOOLEAN,
            "default": False,
        })
        need2render.append({
            "name": "Adaptive_Threshold_Block_Size",
            "type": INT,
            "default": 9,
        })
        need2render.append({
            "name": "C",
            "type": INT,
            "default": 2,
        })
        return need2render

    def cartoonise(self, img_rgb, num_down, num_bilateral, medianBlur, D, sigmaColor, sigmaSpace):
        # 用高斯金字塔降低取样
        img_color = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        for _ in range(num_down):
            img_color = cv2.pyrDown(img_color)
        # 重复使用小的双边滤波代替一个大的滤波
        for _ in range(num_bilateral):
            img_color = cv2.bilateralFilter(img_color, d=D, sigmaColor=sigmaColor, sigmaSpace=sigmaSpace)
        # 升采样图片到原始大小
        for _ in range(num_down):
            img_color = cv2.pyrUp(img_color)
        if not self.Save_Edge:
            img_cartoon = img_color
        else:
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            img_blur = cv2.medianBlur(img_gray, medianBlur)
            img_edge = cv2.adaptiveThreshold(img_blur, 255,
                                             cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY,
                                             blockSize=self.Adaptive_Threshold_Block_Size,
                                             C=self.C)
            img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)
            img_edge = cv2.resize(img_edge, img_color.shape[:2][::-1])
            img_cartoon = cv2.bitwise_and(img_color, img_edge)
        return cv2.cvtColor(img_cartoon, cv2.COLOR_RGB2BGR)

    def transform(self, frame):
        return self.cartoonise(frame, self.num_down, self.num_bilateral, \
                               self.mbk, self.D, self.Sigma_Coloe, self.Sigma_Space)

    def name(self):
        return "cartoon"
