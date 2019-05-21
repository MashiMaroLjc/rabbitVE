import cv2
from skimage.measure import compare_ssim
import scipy


def read_img(path):
    return scipy.misc.imread(path)


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

# if __name__ == "__main__":
#     a = cv2.imread("./test/raw/2.png")
#     a = cv2.resize(a, (256, 256))
#     b = cv2.imread("./test/raw/3.png")
#     b = cv2.resize(b, (256, 256))
#     ssim_value = calc_ssim(a, b)
#     print(ssim_value)
