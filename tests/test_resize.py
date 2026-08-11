import cv2
from cv2.typing import MatLike
from manga2anki.core.speech_bubble import preprocess
import os

def main():
    file_path = "sample/yfnu7-7.png" 
    image = cv2.imread(file_path)
    if image is None:
        print("no image lol")
        return
    cubic_crops = get_bubbles_cubic(image)

    base_name = os.path.basename(file_path)

    for i in range(len(cubic_crops)):
        no_ext_path, file_ext = base_name.split(".", maxsplit=1)
        output_file_name = "./tests/cubic/" + no_ext_path + f"({i})." + file_ext
        if not cv2.imwrite(output_file_name, cubic_crops[i]):
            print("write failed")

def get_bubbles_linear(
        image: MatLike,
        simple_method: bool = True,
) -> list[MatLike]:
    """Returns list of cropped sub-images of areas where text is found."""
    prepped_image = preprocess(image, simple_method)
    # find contours
    contours = cv2.findContours(
        prepped_image,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE,
    )[0]
    cropped_images: list[MatLike] = []
    cropped_image_dims: list[tuple[int, int, int, int]] = []

    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)

        # filter out speech bubbles with unreasonable size
        if (60 < w < 400) and (25 < h < 500):
            cropped_images.append(image[y:y+h, x:x+w])
            cropped_image_dims.append((x, y, x+w, y+h))

    resized_crops = resize_crops_linear(cropped_images)

    return resized_crops

def get_bubbles_lanczos(
        image: MatLike,
        simple_method: bool = True,
) -> list[MatLike]:
    """Returns list of cropped sub-images of areas where text is found."""
    prepped_image = preprocess(image, simple_method)
    # find contours
    contours = cv2.findContours(
        prepped_image,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE,
    )[0]
    cropped_images: list[MatLike] = []
    cropped_image_dims: list[tuple[int, int, int, int]] = []

    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)

        # filter out speech bubbles with unreasonable size
        if (60 < w < 400) and (25 < h < 500):
            cropped_images.append(image[y:y+h, x:x+w])
            cropped_image_dims.append((x, y, x+w, y+h))

    resized_crops = resize_crops_lanczos(cropped_images)

    return resized_crops

def get_bubbles_cubic(
        image: MatLike,
        simple_method: bool = True,
) -> list[MatLike]:
    """Returns list of cropped sub-images of areas where text is found."""
    prepped_image = preprocess(image, simple_method)
    # find contours
    contours = cv2.findContours(
        prepped_image,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE,
    )[0]
    cropped_images: list[MatLike] = []
    cropped_image_dims: list[tuple[int, int, int, int]] = []

    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)

        # filter out speech bubbles with unreasonable size
        if (60 < w < 400) and (25 < h < 500):
            cropped_images.append(image[y:y+h, x:x+w])
            cropped_image_dims.append((x, y, x+w, y+h))

    resized_crops = resize_crops_cubic(cropped_images)

    return resized_crops 

def resize_crops_linear(cropped_images: list[MatLike], scale_factor: int = 2) -> list[MatLike]:
    resized_images: list[MatLike] = []
    for image in cropped_images:
        height, width = image.shape[:2]
        resized_image: MatLike = cv2.resize(
            image,
            (width * scale_factor, height * scale_factor),
            interpolation=cv2.INTER_LINEAR
        )
        resized_images.append(resized_image)
    return resized_images

def resize_crops_lanczos(cropped_images: list[MatLike], scale_factor: int = 2) -> list[MatLike]:
    resized_images: list[MatLike] = []
    for image in cropped_images:
        height, width = image.shape[:2]
        resized_image: MatLike = cv2.resize(
            image,
            (width * scale_factor, height * scale_factor),
            interpolation=cv2.INTER_LANCZOS4
        )
        resized_images.append(resized_image)
    return resized_images

def resize_crops_cubic(cropped_images: list[MatLike], scale_factor: int = 2) -> list[MatLike]:
    resized_images: list[MatLike] = []
    for image in cropped_images:
        height, width = image.shape[:2]
        resized_image: MatLike = cv2.resize(
            image,
            (width * scale_factor, height * scale_factor),
            interpolation=cv2.INTER_CUBIC
        )
        resized_images.append(resized_image)
    return resized_images

if __name__ == "__main__":
    main()