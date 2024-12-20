from haystack import component
from haystack.dataclasses import Document
from .utils import url_basename
import os

@component
class DocIdIndexer():
    """
    Given a list of documents create a dictionary for the documents in the
    list indexed by id.
    """
    def __init__(self):
        pass
    
    @component.output_types(ids=list[str])
    def run(self, documents: list[Document]) -> dict[str, list[str]]:
        return {'ids': [doc.id for doc in documents]}
