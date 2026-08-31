import torch
import torchvision
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from PIL import Image
from PIL.Image import Resampling

# potential better idea for deduplicating instead of NMS:
# detect boxes that intersect, and if one is contained in the other then keep only one of them

class BubbleDetectionEngine:
    def __init__(
            self,
            device: str,
            model_name: str = "ogkalu/comic-text-and-bubble-detector"
            ) -> None:
        if device != "cpu":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device("cpu")

        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModelForObjectDetection.from_pretrained(model_name).to(self.device)

    def detect_bubbles(self, image: Image.Image) -> list[Image.Image]:
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        target_sizes = torch.tensor([image.size[::-1]]).to(self.device)

        results = self.processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=0.5
        )[0]

        iou_threshold = 0.1

        keep_indices: torch.Tensor = torchvision.ops.nms(
            boxes=results["boxes"],
            scores=results["scores"],
            iou_threshold=iou_threshold,
        )

        kept_boxes = results["boxes"][keep_indices]

        crops: list[Image.Image] = []

        boxes: list[tuple[int, int, int, int]] = []

        for detection_region in kept_boxes.tolist():
            box = tuple(int(coord) for coord in detection_region)
            if len(box) != 4:
                raise Exception("invalid coordinates")
            boxes.append(box)

        for box in boxes:
            crop = image.crop(box)
            crops.append(crop)

        resized_crops: list[Image.Image] = resize_pil_crops(crops)

        return resized_crops

def resize_pil_crops(
    cropped_images: list[Image.Image],
    scale_factor: int = 2
    ) -> list[Image.Image]:
    resized_images: list[Image.Image] = []
    for image in cropped_images:
        scaled_dims: tuple[int, int] = (image.width * scale_factor, image.height * scale_factor)
        resized_image = image.resize(scaled_dims, resample=Resampling.LANCZOS)
        resized_images.append(resized_image)
    return resized_images