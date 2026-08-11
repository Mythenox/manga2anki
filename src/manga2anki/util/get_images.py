from pathlib import Path

def get_all_images(path_str: str) -> list[str]:
    valid_exts: set[str] = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp", ".avif"}

    if not Path(path_str).exists():
            return []

    if Path(path_str).is_file():
        if Path(path_str).suffix.lower() in valid_exts:
            return [path_str]
        else:
            return []

    dir_path = Path(path_str)
        
    image_paths = [
        str(filepath) for filepath in dir_path.iterdir() 
        if filepath.is_file() and filepath.suffix.lower() in valid_exts
    ]

    return image_paths