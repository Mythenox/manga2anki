from manga2anki.core.speech_bubble import get_bubbles, detect_bubbles
import cv2
from PIL import Image

def main():
    path = "sample/other/DLRAW.AC_009.jpg"

    img = Image.open(path).convert("RGB")
    if img is None:
        print("error reading image")
        return

    bubbles = detect_bubbles(img)

    for i in range(len(bubbles)):
        filename = f"sample/009-crops-torch/pg9-{i}.jpg"
        bubbles[i].save(filename)

if __name__ == "__main__":
    main()