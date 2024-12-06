import os
from pathlib import Path


def num_files_in_dir(directory):
    return len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])


def save_image(image, path, name):
    path = Path(path).expanduser().resolve().absolute()

    if not path.parent.exists():
        parth.parent.mkdir(parents=True, exist_ok=True)
