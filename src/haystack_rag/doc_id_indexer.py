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
    
    @component.output_types(documents=dict[str, Document], ids=list[str])
    def run(self, documents: list[Document]) -> dict[str, any]:
        docs = { doc.id: doc for doc in documents }
        return {'documents': docs, 'ids':list(docs.keys())}
