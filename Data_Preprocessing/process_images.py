import cv2
import argparse
from pathlib import Path
import os
from csv_editor import resize_bbs_in_csv, replace_images_with_crops_in_csv



def get_new_dims(img, max_h=1248, cnn_input_size=416):
    """
    Computes the width to match the maximum height while keeping the aspect ratio. Then it finds the closest multiple of
     the yolo_dim for this new width.
    :param dims:
    :param max_h:
    :param yolo_dim:
    :return:
    """
    h, w, _ = img.shape
    assert h > max_h, "Height of an image unexpectedly small!"
    factor = h / max_h
    new_w = w / factor
    w_mul = new_w // cnn_input_size
    rem_curr = abs(new_w - w_mul * cnn_input_size)
    rem_next = abs(new_w - (w_mul + 1) * cnn_input_size)
    new_w = w_mul * cnn_input_size if rem_curr < rem_next else (w_mul + 1) * cnn_input_size

    try:
        new_w = int(new_w)
        max_h = int(max_h)
    except ValueError:
        print("Could not convert new image dimensions to integer! Setting them to default size!")
        new_w = int(cnn_input_size)
        max_h = int(2 * cnn_input_size)
    multiplier_w = new_w / w
    multiplier_h = max_h / h
    return new_w, max_h, multiplier_w, multiplier_h

def resize_image_to_dims(img, dims):
    new_w, new_h = dims
    resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    return resized_img

def resize_image_by_multiplier(img, multiplier_w, multiplier_h):
    h, w, _ = img.shape
    resized_img = cv2.resize(img, (w*multiplier_w, h*multiplier_h), interpolation=cv2.INTER_CUBIC)
    return resized_img

def divide_image_into_crops(img, cnn_input_size=416):
    """

    :param img:
    :param cnn_input_size:
    :return: list of 3 element tuples where (image, height span tuple, width span tuple)
    """
    height, width, _ = img.shape
    assert height >= cnn_input_size and width >= cnn_input_size, "One of the image dimensions is too small!"
    crops = []
    height_crops = height // cnn_input_size
    width_crops = width // cnn_input_size
    for h in range(height_crops):
        for w in range(width_crops):
            h_span = (h*cnn_input_size, (h+1)*cnn_input_size)
            w_span = (w*cnn_input_size, (w+1)*cnn_input_size)
            crops.append((img[h_span[0]:h_span[1], w_span[0]:w_span[1]], h_span, w_span))
    return crops

def replace_image_with_crops(image_path, crops):
    """

    :param image_path:
    :param crops:
    :return: Three dictionaries:
    1. Dictionary mapping from the newly created image crop names to the crop objects
    2. Dictionary mapping from the cropped image name to the original image name
    3. Dictionary mapping from the original image name to all of its crops
    """
    image_dir = os.path.dirname(image_path)
    basename = os.path.splitext(os.path.basename(image_path))
    basename_wo_ext = basename[0]
    ext = basename[1]
    file_name_to_crops = {}
    crop_names_to_orig_names = {}
    orig_names_to_crop_names = {}

    for i, crop in enumerate(crops):
        crop_name = "".join([basename_wo_ext, "_crop_", str(i), ext])
        file_name_to_crops[crop_name] = crop
        crop_names_to_orig_names[crop_name] = basename_wo_ext
        if basename_wo_ext not in orig_names_to_crop_names.keys():
            orig_names_to_crop_names[basename_wo_ext] = [crop_name]
        else:
            orig_names_to_crop_names[basename_wo_ext].append(crop_name)
        crop_path = os.path.join(image_dir, crop_name)
        print(f"Saving {crop_path}")
        cv2.imwrite(crop_path, crop[0])

    # try:
    #     os.remove(image_path)
    # except OSError:
    #     print(f"Failed to remove {image_path}")
    return file_name_to_crops, crop_names_to_orig_names, orig_names_to_crop_names


def process_image(image_path):
    """Main function representing the processing pipeline for a singe image."""
    img = cv2.imread(image_path)
    new_width, new_height, width_multiplier, height_multiplier = get_new_dims(img, 1248, 416)
    resized_image = resize_image_to_dims(img, (new_width, new_height))
    crops = divide_image_into_crops(resized_image)
    names_to_crops, crop_to_orig, orig_to_crop = replace_image_with_crops(image_path, crops)
    replace_images_with_crops_in_csv(image_path, names_to_crops, crop_to_orig, orig_to_crop)
    #resize_bbs_in_csv(image_path, width_multiplier, height_multiplier)

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
        process_image(image_path)