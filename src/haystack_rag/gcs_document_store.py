from typing import List, Dict, Any
from google.cloud import storage
from haystack.dataclasses import Document
import json
import re

class GCSDocumentStore:
    """
    Document store that use a google S3 account, support query only by id.
    """

    def __init__(self, bucket_name: str, project_id: str):
        self._client = storage.Client(project=project_id)
        self._bucket = self._client.bucket(bucket_name)
        self._blob_name_pattern = 'docs/{id}.json'
        regex_pattern = self._blob_name_pattern.replace("{id}", r"(?P<id>[^/]+)")
        self._blob_pattern = re.compile(regex_pattern)

    def _get_blob_name(self, doc_key: str) -> str:
        return self._blob_name_pattern.format(id=doc_key)

    def _is_document_blob(self, blob_name: str) -> bool:
        return self._blob_pattern.match(blob_name) is not None
    
    def _document_key(doc: Document) -> str:
        doc_key = doc.meta['file_path']
        if not doc_key:
            raise ValueError("Document must have an 'id' field")
        return doc_key

    def count_documents(self, **kwargs) -> int:
        count = sum(1 for blob in self._bucket.list_blobs() if self._is_document_blob(blob.name))
        return count

    def filter_documents(self, filters: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        documents = []
        for blob in self._bucket.list_blobs():
            if self._is_document_blob(blob.name):
                doc_dict = json.loads(blob.download_as_string())
                if all(doc_dict.get(k) == v for k, v in filters.items()):
                    documents.append(doc_dict)
        return documents

    def write_documents(self, documents: List[Dict[str, Any]], **kwargs) -> None:
        for doc in documents:
            doc_key = self._document_key(doc)
            blob_name = self._get_blob_name(doc_key)
            blob = self._bucket.blob(blob_name)
            blob.upload_from_string(json.dumps(doc))

    def delete_documents(self, doc_keys: List[str], **kwargs) -> None:
        for doc_key in doc_keys:
            blob_name = self._get_blob_name(doc_key)
            blob = self._bucket.blob(blob_name)
            if blob.exists():
                blob.delete()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "GCSDocumentStore",
            "project_id": self._client.project,
            "bucket_name": self._bucket.name
        }

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'GCSDocumentStore':
        return cls(
            project_id=config["project_id"],
            bucket_name=config["bucket_name"]
        )