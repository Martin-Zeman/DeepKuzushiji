import cv2
import argparse
from pathlib import Path



def get_new_dims(dims, max_h, yolo_dim):
    """
    Computes the width to match the maximum height while keeping the aspect ratio. Then it finds the closest multiple of
     the yolo_dim for this new width.
    :param dims:
    :param max_h:
    :param yolo_dim:
    :return:
    """
    w, h = dims
    assert h > max_h, "Height of an image unexpectedly small!"
    factor = h / max_h
    new_w = w / factor
    w_mul = new_w // yolo_dim
    rem_curr = abs(new_w - w_mul * yolo_dim)
    rem_next = abs(new_w - (w_mul + 1) * yolo_dim)
    new_w = w_mul * yolo_dim if rem_curr < rem_next else (w_mul + 1) * yolo_dim

    try:
        new_w = int(new_w)
        max_h = int(max_h)
    except ValueError:
        print("Could not convert new image dimensions to integer! Setting them to default size")
        new_w = int(416)
        max_h = int(832)
    return new_w, max_h

def resize_image(img, dims):
    new_w, new_h = dims
    resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    return resized_img

def cropout_of_image(img):
    # TODO
    crop_img = img[0:416, 0:416]
    cv2.imshow("croppped", crop_img)
    cv2.waitKey(0)


def process_image(image_path):
    None
    # Here I will call all the other functions. First open the image. Make sure to include try and except

def define_arguments(parser):
    parser.add_argument("-i", "--image", type=Path,
                        default=Path(__file__).absolute().parent.parent / "Datasets/Japanese_Classics_Preprocessed/200021637/images/200021637-00014_2.jpg",
                        help="Path to the image file")
    return parser

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser = define_arguments(parser)
    args = parser.parse_args()
    try:
        image_path = str(args.image)
    except ValueError:
        print("Cannot convert the path to string!")
    else:
        img = cv2.imread(image_path)
        # cropout_of_image(img)
        height, width, _ = img.shape
        new_width, new_height = get_new_dims((width, height), 1248, 416)
        resized_image = resize_image(img, (new_width, new_height))
        cv2.imwrite("/home/thiscord/Documents/DeepKuzushiji/Datasets/Japanese_Classics_Preprocessed/resized.jpg", resized_image)