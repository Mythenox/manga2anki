import cv2
from cv2.typing import MatLike
from matplotlib import pyplot as plt

# TODO: replace opencv with Pillow for free threading support


def main():
    file_path = "sample/yfnu7-7.png" 
    image = cv2.imread(file_path)
    if image is not None:
        drawn_image, cropped_images = find_bubbles_and_mark(image)
        for i in range(len(cropped_images)):
            no_ext_path, file_ext = file_path.split(".", maxsplit=1)
            output_file_name = no_ext_path + f"({i})." + file_ext
            cv2.imwrite(output_file_name, cropped_images[i])
            print(f'Image "{output_file_name}" has been saved.')
        plot(drawn_image)
    else:
        raise Exception("image not found")
    
def preprocess(image: MatLike, simple_method: bool = True) -> MatLike:
    """Applies greyscale, then Gaussian blur, then Canny edge detection,
    then binarization. Skips Canny edge detection if simple_method argument
    is equal to True. Returns the resulting image."""
    if simple_method:
        processed: tuple[float, MatLike] = (
            cv2.threshold(
                cv2.GaussianBlur(
                    cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),
                    (3,3),
                    0,
                ),
                235,
                255,
                cv2.THRESH_BINARY,
            )
        )
        return processed[1]
    else:
        # for some reason, this gives awful results
        processed = cv2.threshold(
            cv2.Canny(
                cv2.GaussianBlur(
                    cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),
                    (3,3),
                    0,
                ),
                50,
                500,
            ),
            235,
            255,
            cv2.THRESH_BINARY,
        )
        return processed[1]
    

def find_bubbles(
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
    return cropped_images


def find_bubbles_and_mark(
        image: MatLike,
        simple_method: bool = True,
) -> tuple[MatLike, list[MatLike]]:
    """Returns list of cropped sub-images of areas where text is found,
    along with the original image with the crop boundaries drawn on them."""
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
    return draw_to_image(image, cropped_image_dims), cropped_images


def draw_to_image(
        image: MatLike,
        rect_dims: list[tuple[int, int, int, int]],
        color: tuple[int, int, int] = (255, 0, 0),
) -> MatLike:
    """Draws colored rectangles with given dimensions on the given image."""
    if len(rect_dims) == 0:
        return image
    drawn_image = image
    for dims in rect_dims:
        a, b, c, d = dims
        drawn_image = cv2.rectangle(image, (a, b), (c, d), color, 2)
    return drawn_image


def resize_rectangles(
        prepped_image: MatLike,
        rect_dims: list[tuple[int, int, int, int]]
) -> list[tuple[int, int, int, int]]:
    """Shrink rectangles until they no longer overlap each other's areas.
       Since binarization is applied, maybe just shrink until the edges no longer
       intersect black pixels?"""
    # compute farthest speech bubble border,
    pass


def plot(image: MatLike) -> None:
    plt.figure(figsize = (15,20))
    plt.imshow(image)
    plt.axis("off")
    plt.show()
    

if __name__ == "__main__":
    main()