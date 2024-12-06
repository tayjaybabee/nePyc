import os
import imagehash
from io import BytesIO
from nepyc.log_engine import ROOT_LOGGER as PARENT_LOGGER


MOD_LOGGER = PARENT_LOGGER.get_child('server.utils.hashes')


def load_hashes(pic_dir):
    hashes_file = os.path.join(pic_dir, 'hashes.txt')

    if not os.path.exists(hashes_file):
        return set()

    with open(hashes_file, 'r', encoding='utf-8') as f:
        existing_hashes = {line.strip() for line in f if line.strip()}

    return existing_hashes


def load_hash_data(pic_dir):
    hashes_file = os.path.join(pic_dir, 'hashes.txt')
    known_hashes = {}

    if os.path.exists(hashes_file):
        with open(hashes_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()

                    if len(parts) == 2:
                        h, num_str = parts
                        num = int(num_str)
                        known_hashes[h] = num

    token_numbers = set(known_hashes.values())

    if not token_numbers:
        missing_numbers = []
        max_number = 0
    else:
        max_number = max(token_numbers)
        missing_numbers = sorted(set(range(1, max_number + 1)) - token_numbers)

    print(known_hashes, missing_numbers, max_number)

    return known_hashes, missing_numbers, max_number

def append_hash_to_file(pic_dir, hash, number):
    hashes_file = os.path.join(pic_dir, 'hashes.txt')

    with open(hashes_file, 'a', encoding='utf-8') as f:
        f.write(f'{hash} {number}\n')


def check_hash(image, hashes):
    log = MOD_LOGGER.get_child('check_hash')

    hash = imagehash.average_hash(image)

    if hash in hashes:
        log.debug(f'Hash {hash} already exists')
        return True
    else:
        log.debug(f'Hash {hash} does not exist')
        return False
