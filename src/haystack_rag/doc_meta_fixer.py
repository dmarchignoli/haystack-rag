from haystack import component
from haystack.dataclasses import Document
from .utils import url_basename
import os

@component
class DocMetaFixer():
    """
    Add url meta field using file_path meta field and a list of possible url
    """
    def __init__(self):
        pass
    
    @component.output_types(documents=list[Document])
    def run(self, documents: list[Document], origin_urls: list[str]) -> dict[str, list[Document]]:
        url_by_path = { url_basename(x): x for x in origin_urls }
        for doc in documents:
            url = url_by_path[os.path.basename(doc.meta['file_path'])]
            doc.meta['url'] = url
        return {'documents': documents}
