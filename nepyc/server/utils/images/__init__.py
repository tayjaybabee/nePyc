import hashlib
import os
from nepyc.server.utils.hashes import load_hashes
from PIL import Image



def assign_number(missing_numbers, max_number):
    if missing_numbers:
        return missing_numbers.pop(), max_number

    return max_number + 1, max_number + 1


def load_all_images(pic_dir):
    images = []
    for file_name in os.listdir(pic_dir):
        if file_name.endswith('.png'):
            file_path = os.path.join(pic_dir, file_name)
            images.append(Image.open(file_path))

    return images


def save_unique(images, pic_dir):
    os.makedirs(pic_dir, exist_ok=True)

    known_hashes, missing_numbers, max_number = load_hashes(pic_dir)

    for img in images:

        img_bytes = img.tobytes()

        img_hash  = hashlib.md5(img_bytes).hexdigest()

        if img_hash not in known_hashes:

            file_number, max_number = assign_number(missing_numbers, max_number)
            file_name = f'{file_number}.png'
            file_path = os.path.join(pic_dir, file_name)

            img.save(file_path)

            known_hashes[img_hash] = file_number
            append_hash_to_file(pic_dir, img_hash, file_number)
