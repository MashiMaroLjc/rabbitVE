import cv2
from skimage.measure import compare_ssim
import yaml
import os

class HistSort:
    def __init__(self, from_path, to_path):
        self.from_path = from_path
        self.to_path = to_path

    def sort(self):
        img_path = [x.path for x in os.scandir(self.from_path) if
                    x.path.endswith("jpg") or x.path.endswith("png") or x.path.endswith("jpeg")]
        img_list = [
            [img, cv2.calcHist([cv2.imread(img)], [0], None, [256], [0, 256])]
            for img in img_path
        ]
        img_list_len = len(img_list)
        for i in range(0, img_list_len - 1):
            min_score = float("inf")
            j_min_score = i + 1
            for j in range(i + 1, len(img_list)):
                score = cv2.compareHist(img_list[i][1],
                                        img_list[j][1],
                                        cv2.HISTCMP_BHATTACHARYYA)
                if score < min_score:
                    min_score = score
                    j_min_score = j
            (img_list[i + 1],
             img_list[j_min_score]) = (img_list[j_min_score],
                                       img_list[i + 1])
        for i, item in enumerate(img_list):
            img = cv2.imread(item[0])
            path = os.path.join(self.to_path, "{}.png".format(i + 1))
            cv2.imwrite(path, img)
            print("Save in ", path)


#
# def read_img(path):
#     return scipy.misc.imread(path)


def load_config(path):
    return yaml.load(open(path, encoding='utf-8'))

def second_format(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


def calc_ssim(a, b):
    ssim = compare_ssim(cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), cv2.cvtColor(b, cv2.COLOR_BGR2GRAY))
    return ssim


def compareHist(a, b):
    a_hist = cv2.calcHist([a], [0], None, [256], [0, 256])
    b_hist = cv2.calcHist([b], [0], None, [256], [0, 256])
    return cv2.compareHist(a_hist,b_hist,cv2.HISTCMP_BHATTACHARYYA)




def detect_face(img, model, max_v):
    h, w, c = img.shape
    if max([h, w]) > max_v:
        if h > w:
            scale = max_v / h
            nw = int(w * scale)
            nh = max_v
        else:
            scale = max_v / w
            nh = int(h * scale)
            nw = max_v
        img = cv2.resize(img, (nw, nh))
    _, faces = model.detecte(img)
    return img, faces



calc_continue_func_dict = {
    "hist":compareHist,
}
# if __name__ == "__main__":
#     a = cv2.imread("./test/raw/2.png")
#     a = cv2.resize(a, (256, 256))
#     b = cv2.imread("./test/raw/3.png")
#     b = cv2.resize(b, (256, 256))
#     ssim_value = calc_ssim(a, b)
#     print(ssim_value)
