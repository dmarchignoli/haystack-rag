
from typing import List
from urllib.parse import urlparse

import os

BASE_DIR='.'

def load_library_urls() -> List[str]:
    with open(os.path.join(BASE_DIR, 'resources/library_urls.txt')) as f:
        return [x.strip() for x in f.readlines()]

def url_basename(url: str) -> str:
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if not filename:  # Handle cases where there's no filename in the URL
        raise ValueError("Missing base name in {url}")
    return filename