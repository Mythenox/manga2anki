import cv2
from cv2.typing import MatLike
from manga_ocr import MangaOcr
import PIL
from PIL import Image
from manga2anki.util.speech_bubble import find_bubbles, preprocess

#TODO: use multiprocessing?


def main():
    images = [f"sample/yfnu7-7({i}).png" for i in range(13)]
    text_list = get_bubble_text(images)
    print(len(text_list))
    

def resize_crops(cropped_images: list[MatLike], scale_factor: int = 2) -> list[MatLike]:
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


def get_bubble_text(cropped_images) -> list[str]:
    mocr = MangaOcr()
    bubble_texts: list[str] = []
    for image in cropped_images:
        bubble_text = mocr(image)
        bubble_texts.append(bubble_text)
    return bubble_texts


if __name__ == "__main__":
    main()