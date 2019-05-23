from . import cvdnn, dlib_cnn, dlib_hog

detector_dict = {
    "cvdnn": cvdnn.CVDNN,
    "dlib_cnn": dlib_cnn.DLIBCNN,
    "dlib_hog": dlib_hog.DLIBHOG
}
