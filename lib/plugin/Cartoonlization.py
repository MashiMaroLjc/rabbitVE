from .BasePlugin import BasePlugin
from .param_type import *
import cv2


class Cartoonlization(BasePlugin):
    def __init__(self):
        super(Cartoonlization,self).__init__()

    def initialize(self, params):
        self.num_down = params["Num_Down"]
        self.num_bilateral = params["Num_Bilateral"]
        self.mbk = params["Median_Blur_Kernel"]

    def render_info(self):
        """
        #  list item(dict) 的key（可选） name type option default
        :return: a class extend tk.Toplevel  or list
        """
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
        return need2render

    def cartoonise(self, img_rgb, num_down, num_bilateral, medianBlur):
        # 用高斯金字塔降低取样
        img_color = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        for _ in range(num_down):
            img_color = cv2.pyrDown(img_color)
        # 重复使用小的双边滤波代替一个大的滤波
        for _ in range(num_bilateral):
            img_color = cv2.bilateralFilter(img_color, d=9, sigmaColor=9, sigmaSpace=7)
        # 升采样图片到原始大小
        for _ in range(num_down):
            img_color = cv2.pyrUp(img_color)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        img_blur = cv2.medianBlur(img_gray, medianBlur)
        img_edge = cv2.adaptiveThreshold(img_blur, 255,
                                         cv2.ADAPTIVE_THRESH_MEAN_C,
                                         cv2.THRESH_BINARY,
                                         blockSize=9,
                                         C=2)
        img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)
        img_edge = cv2.resize(img_edge, img_color.shape[:2][::-1])
        img_cartoon = cv2.bitwise_and(img_color, img_edge)
        return cv2.cvtColor(img_cartoon, cv2.COLOR_RGB2BGR)

    def transform(self, frame):
        return self.cartoonise(frame, self.num_down, self.num_bilateral, self.mbk)

    def name(self):
        return "cartoon"
