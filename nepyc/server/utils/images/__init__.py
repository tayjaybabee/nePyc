import hashlib
import os
from nepyc.server.utils.hashes import load_hashes
from PIL import Image
import shutil
from zipfile import ZipFile
from rich.console import Console
from pathlib import Path
from tqdm import tqdm
from inspyre_toolbox.path_man import provision_path
from tempfile import TemporaryDirectory


CONSOLE = Console()
EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.jfif']


def backup_images(
        image_dir,
        backup_dir=None,
        with_progress=False,
        delete_after=False,
        as_archive=False,
        **kwargs
):
    image_dir = provision_path(image_dir)

    if not image_dir.exists():
        raise FileNotFoundError(f'Image directory not found: {image_dir}')

    if backup_dir is None:
        backup_dir = image_dir / 'backup'

    backup_dir = provision_path(backup_dir)

    if not backup_dir.exists():
        backup_dir.mkdir(parents=True)

    image_files = get_image_files(image_dir)

    if not image_files:
        return

    if with_progress:
        steps = ['Copying'] if not as_archive else ['Archiving']
        images = tqdm(image_files, desc='Backing')


def delete_all_images(
        image_dir,
        backup=False,
        with_progress=False,
        raise_on_error=False,
        **kwargs
):
    image_dir = Path(image_dir).expanduser()

    if backup:
        backup_images(image_dir, backup_dir=kwargs.pop('backup_dir', None), with_progress=with_progress, delete_after=False, as_archive=kwargs.pop('as_archive', False), **kwargs)

    image_files = get_image_files(image_dir)

    if not image_files:
        return

    if with_progress:
        images = tqdm(image_files, desc='Deleting images', total=len(image_files), unit='file', ncols=100)
    else:
        images = image_files

    for image in images:
        try:
            os.remove(image)
            CONSOLE.print(f'[bold][green]Deleted[/bold]: {image}[/green]')

            if with_progress:
                images.set_description(f'Deleting images: {os.path.basename(image)}')
                images.update(1)
        except Exception as e:
            CONSOLE.print(f'[bold][red]Error[/bold]: {e}[/red]')
            if not raise_on_error:
                continue
            else:
                raise e from e

    CONSOLE.print(f'[bold][green]Deleted[/bold]: {len(image_files)} images from {image_dir}[/green]')


def get_file_hash(file_path, chunk_size=1024*1024):
    hash_md5 = hashlib.md5()

    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def get_image_files(directory):
    files = []

    all_files = os.walk(directory)

    for root, _, c_files in all_files:
        for file in c_files:
            if any(file.lower().endswith(ext) for ext in EXTENSIONS):
                files.append(os.path.join(root, file))

    return files


def copy_all_images(pic_dir, dest_dir, keep_names=False, with_progress=False):
    os.makedirs(dest_dir, exist_ok=True)

    images = load_all_images(pic_dir)

    iter_img = enumerate(images) if not with_progress else tqdm(enumerate(images), total=len(images), desc='Copying images', unit='file', ncols=100)

    for i, img in iter_img:
        if keep_names:
            img.save(os.path.join(dest_dir, f'{i}.png'))
        else:
            img.save(os.path.join(dest_dir, f'{i}.png'))


def archive_images(directory, archive_name, delete_after=False, with_progress=False, validate=False):
    image_files = get_image_files(directory)

    with ZipFile(archive_name, 'w') as archive:
        image_files = tqdm(image_files, desc='Archiving images', unit='file', ncols=100) if with_progress else image_files

        for image in image_files:
            archive.write(image, os.path.relpath(image, directory))

            CONSOLE.print(f'[bold][green]Archived[/bold]: {image}[/green]')

            if with_progress:
                image_files.set_description(f'Archiving images: {os.path.basename(image)}')
                image_files.update(1)

    CONSOLE.print(f'[bold] [green]Archived[/bold]: {len(image_files)} images to {archive_name}[/green]')

    if validate:
        if not validate_archive(archive_file_name, image_filesimage_files):
            CONSOLE.print(f'[bold][red]Validation failed[/bold]: {archive_name}')
            return False
        else:
            CONSOLE.print(f'[bold][green]Archive validated[/bold]: {archive_name}')

            if delete_after:
                for image in image_files:
                    os.remove(image)
                    CONSOLE.p




def assign_number(missing_numbers, max_number):
    if missing_numbers:
        return missing_numbers.pop(), max_number

    return max_number + 1, max_number + 1


def get_destination_paths(source_dir, dest_dir, rename=False, prefix='image_'):
    image_files = get_image_files(source_dir)
    destination_paths = {}

    for i, image_file in enumerate(image_files):
        base_name = os.path.basename(image_file)
        name, ext = os.path.splitext(base_name)

        if rename:
            new_name = f'{prefix}{i+1}{ext}'
            new_path = os.path.join(dest_dir, new_name)
            destination_paths[image_file] = new_path
        else:
            new_path = os.path.join(dest_dir, base_name)
            destination_paths[image_file] = new_path

    return destination_paths


def load_all_images(pic_dir):
    images = []
    for file_name in os.listdir(pic_dir):
        if file_name.endswith('.png'):
            file_path = os.path.join(pic_dir, file_name)
            images.append(Image.open(file_path))

    return images


def move_images(source_dir, dest_dir, rename=False, prefix='image', with_progress=False, validate=False,
                chunk_size=1024 * 1024):
    """
    Moves all images from the source directory to the destination directory, with the option to rename them.
    Validates each file after moving if `validate=True`.

    Parameters:
        source_dir (str): The source directory to move the images from.
        dest_dir (str): The destination directory to move the images to.
        rename (bool, optional): If True, the images will be renamed with a prefix. Defaults to False.
        prefix (str, optional): The prefix to use for the renamed images. Defaults to 'image'.
        with_progress (bool, optional): If True, a progress bar will be displayed. Defaults to False.
        validate (bool, optional): If True, files will be validated after moving. Defaults to False.
        chunk_size (int, optional): The chunk size to read while moving files. Defaults to 1 MB.

    Returns:
        None
    """
    image_files = get_image_files(source_dir)

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    destination_paths = get_destination_paths(source_dir, dest_dir, rename, prefix)

    if with_progress:
        overall_progress = tqdm(total=len(image_files), desc='Moving images', unit='file', ncols=100)

    for i, image_file in enumerate(image_files):
        # Build full destination path
        dest_file = destination_paths[image_file]

        if with_progress:
            with tqdm(total=1, desc=f'Processing {os.path.basename(image_file)}', leave=False,
                      ncols=100) as photo_progress:
                if not move_image(image_file, dest_file, with_progress, validate, chunk_size):
                    continue  # Skip this file if validation failed
                photo_progress.update(1)
        else:
            if not move_image(image_file, dest_file, with_progress, validate, chunk_size):
                continue  # Skip this file if validation failed

        if with_progress:
            overall_progress.update(1)

    if with_progress:
        overall_progress.close()

    CONSOLE.print(f'[bold green]Moved[/bold]: {len(image_files)} images from {source_dir} to {dest_dir}[/green]')


def move_image(
        source_file,
        dest_file,
        with_progress=False,
        validate=False,
        chunk_size=1024*1024,
):
    from pathlib import Path

    base_name = os.path.basename(source_file)
    name, ext = os.path.splitext(base_name)

    source_path = Path(source_file).expanduser().resolve()
    dest_path = Path(dest_file).expanduser().resolve()
    dest_dir = dest_path.parent

    if not dest_dir.exists():
        dest_dir.mkdir(parents=True)

    size = os.path.getsize(source_file)

    if with_progress:
        with tqdm(total=size, desc=f'Processing {base_name}', unit='B', unit_scale=True, ncols=100) as file_progress:
            with open(source_file, 'rb') as src_file, open(dest_file, 'wb') as dst_file:

                # Copy chunks and update the progress bar.
                while chunk := src_file.read(chunk_size):
                    dst_file.write(chunk)
                    file_progress.update(len(chunk))

    else:
        shutil.move(source_file, dest_file)

    if validate:
        if not validate_file(source_file, dest_file, chunk_size):
            CONSOLE.print(f'[bold red]Validation failed[/bold]: {source_file} -> {dest_file} (Hash mismatch!)')
            return False
        CONSOLE.print(f'[bold green]File validated[/bold]: {base_name}')
    else:
        CONSOLE.print(f'[bold green]Moved[/bold]: {base_name}')

    return True




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


def validate_archive(archive_file_path, original_files):
    with zipfile.ZipFile(archive_file_path, 'r') as archive:
        with TemporaryDirectory() as temp_dir:
            for file in original_files:
                extracted_path = os.path.join(temp_dir, os.path.relpath(file, start=os.path.dirname(file)))

                archive.extract(file, temp_dir)

                if not validate_file(file, extracted_path):
                    CONSOLE.print(f'[bold][red]Validation failed[/bold]: {file} -> {extracted_path} (Hash mismatch!)')
                    return False

    return True


def validate_file(source_file, dest_file, chunk_size=1024*1024):
    source_hash = get_file_hash(source_file, chunk_size)
    dest_hash = get_file_hash(dest_file, chunk_size)

    if source_hash == dest_hash:
        return True
    else:
        CONSOLE.print(f'[bold red]Validation failed[/bold]: {source_file} -> {dest_file} (Hash mismatch!)')
        return False
