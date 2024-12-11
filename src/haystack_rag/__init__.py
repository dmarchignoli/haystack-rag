from .gcs_document_store import GCSDocumentStore
from .byte_stream_serializer import ByteStreamMaterializer

import os

BASE_DIR='.'

def load_library_urls():
    with open(os.path.join(BASE_DIR, 'resources/library_urls.txt')) as f:
        return [x.strip() for x in f.readlines()]

