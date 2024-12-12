from haystack import component
from haystack.dataclasses import Document
from .utils import url_basename

CACHE_SUBDIR = '.cache/haystack'

@component
class DocMetaFixer():
    """
    Add url meta field using file_path meta field and a list of possible url
    """
    def __init__(self):
        pass
    
    @component.output_types(documents=list[Document])
    def run(self, documents: list[Document], origin_urls: list[str]) -> list[Document]:
        url_by_path = { url_basename(x): x for x in origin_urls }
        for doc in documents:
            url = url_by_path[doc.meta['file_path']]
            doc['url'] = url
        return documents
