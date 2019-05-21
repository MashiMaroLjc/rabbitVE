#
# 对图片按照一定的规则进行排序，方便人工去除不合适的图片
#
import cv2
import os
import argparse


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--src', type=str,
                        help='path of face need to sort (default: ./face)', default="./face")
    parser.add_argument('-t', '--target', type=str,
                        help='path of output face (default: ./face)', default="./face")
    parser.add_argument('--type', type=str, help='the type of sort(default:hist)', default="hist", choices=("hist",))
    args = parser.parse_args()
    if not os.path.exists(args.target):
        os.makedirs(args.target)
    if args.type == "hist":
        HistSort(args.src, args.target).sort()
