from haystack import component
from haystack.dataclasses import Document
from .utils import url_basename
import os

@component
class DocIdFilter():
    """
    Given a list of documents create a dictionary for the documents in the
    list indexed by id.
    """
    def __init__(self):
        pass
    
    @component.output_types(documents=list[Document])
    def run(self, documents: list[Document], ids:list[str]) -> dict[str, list[Document]]:
        filter_ids = {doc.id for doc in documents}
        return {'documents': [doc for doc in documents if doc.id in filter_ids]}
