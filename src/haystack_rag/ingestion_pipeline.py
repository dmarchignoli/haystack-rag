from haystack import Pipeline
from haystack.components.fetchers import LinkContentFetcher
from haystack_rag import GCSDocumentStore
from haystack_rag import DocIdIndexer, DocIdFilter
from haystack.components.caching import CacheChecker
from haystack.components.writers import DocumentWriter
from haystack.components.joiners.document_joiner import DocumentJoiner
from haystack.components.joiners import BranchJoiner
from haystack.components.converters import PDFMinerToDocument
from haystack.components.preprocessors import DocumentCleaner
from haystack.components.preprocessors import NLTKDocumentSplitter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy

# cfg = {
#     "gcs_docs_store": {
#         # Google cloud project used for S3 stora
#         "project_id": "cellular-ring-443811-t2",
#         # Google cloud storage bucket
#         "bucket_name": "haystack-docs-826421350323",
#     },
#     "splitter": {
#         "split_by": "sentence",
#         "split_length": 5,
#         "split_overlap": 1,
#         "language": "it",
#     },
#     "embedding": {
#         "dim": 896,
#         "model": "HIT-TMG/KaLM-embedding-multilingual-mini-instruct-v1"
#     },
#     "qdrant_chunks_store": {
#         "url": "https://78684256-5f96-47e6-9691-c5a9efc8d97c.eu-central-1-0.aws.cloud.qdrant.io:6333",
#         "api_key": Secret.from_token(userdata.get('QDRANT_API_KEY')),
#         "similarity": "cosine",
#         "index": "haystack-rag",
#         "recreate_index": False,
#     },
#     "writer": {
#         "policy": DuplicatePolicy.OVERWRITE
#     }
# }

def ingestion_pipeline(config: dict) -> Pipeline:
    gcs_config = config["gcs_docs_store"]
    docs_store = GCSDocumentStore(
        project_id=gcs_config["project_id"],
        bucket_name=gcs_config["bucket_name"])

    qdrant_config = config["qdrant_chunks_store"]
    chunks_store = QdrantDocumentStore(
        url=qdrant_config["url"],
        api_key = qdrant_config["api_key"],
        embedding_dim=config["embedding"]["dim"],
        similarity=qdrant_config.get("similarity", "cosine"),
        index=qdrant_config["index"],
        recreate_index=qdrant_config.get("recreate_index", False),
    ) # type: ignore

    pipeline = Pipeline()

    docs_cache_checker = CacheChecker(document_store=docs_store, cache_field="url") #type: ignore
    pipeline.add_component(instance=docs_cache_checker, name="docs_cache_checker")

    fetcher = LinkContentFetcher() # type: ignore
    pipeline.add_component(instance=fetcher, name="fetcher")
    pipeline.connect("docs_cache_checker.misses", "fetcher")

    converter = PDFMinerToDocument() #type: ignore
    pipeline.add_component(instance=converter, name="converter")
    pipeline.connect("fetcher", "converter")

    docs_writer = DocumentWriter(document_store=docs_store) #type: ignore
    pipeline.add_component(instance=docs_writer, name="docs_writer")
    pipeline.connect("converter", "docs_writer")

    docs_joiner = DocumentJoiner(join_mode="concatenate") #type: ignore
    pipeline.add_component(instance=docs_joiner, name="docs_joiner")
    pipeline.connect("docs_writer", "docs_joiner")
    pipeline.connect("docs_cache_checker.hits", "docs_joiner")

    cleaner = DocumentCleaner(remove_regex=r"\A[0-9]+\Z") #type: ignore
    pipeline.add_component(instance=cleaner, name="cleaner")
    pipeline.connect("docs_joiner", "cleaner")

    splitter = NLTKDocumentSplitter(split_by="sentence", split_length=5, \
                                    split_overlap=1, language="it") #type: ignore
    pipeline.add_component(instance=splitter, name="splitter")
    pipeline.connect("cleaner", "splitter")

    chunks_id_extractor = DocIdIndexer() #type: ignore
    pipeline.add_component(instance=chunks_id_extractor, name="chunks_id_extractor")
    pipeline.connect("splitter", "chunks_id_extractor")

    chunks_cache_checker = CacheChecker(document_store=chunks_store, cache_field="id") #type: ignore
    pipeline.add_component(instance=chunks_cache_checker, name="chunks_cache_checker")
    pipeline.connect("chunks_id_extractor", "chunks_cache_checker")

    missing_chunks_filter = DocIdFilter() #type: ignore
    pipeline.add_component(instance=missing_chunks_filter, name="missing_chunks_filter")
    pipeline.connect("chunks_cache_checker.misses", "missing_chunks_filter.ids")
    pipeline.connect("splitter", "missing_chunks_filter.documents")

    model_name=config["embedding"]["model"]
    embedder = SentenceTransformersDocumentEmbedder(model=model_name) #type: ignore
    pipeline.add_component(instance=embedder, name="embedder")
    pipeline.connect("missing_chunks_filter", "embedder")

    writer = DocumentWriter(document_store=chunks_store,
                            policy=DuplicatePolicy.OVERWRITE) #type: ignore
    pipeline.add_component(instance=writer, name="writer")
    pipeline.connect("embedder", "writer")

    return pipeline
