
import os
from typing import List, Optional
from haystack import component
from haystack.dataclasses import ByteStream
from pathlib import Path
from urllib.parse import urlparse
#from haystack.components.fetchers import LinkContentFetcher
#from haystack_integrations.components.converters.unstructured import UnstructuredFileConverter, UNSTRUCTURED_HOSTED_API_URL

BASE_DIR='.'

def load_library_urls():
    with open(os.path.join(BASE_DIR, 'resources/library_urls.txt')) as f:
        return [x.strip() for x in f.readlines()]


CACHE_SUBDIR = '.cache/haystack'

@component
class ByteStreamMaterializer():
    """
    Saves the byte streams in input to filesystem returns the file paths
    """
    def __init__(self, out_dir: Optional[Path] = None):
        if out_dir is None:
            out_dir = os.path.join(os.getenv('HOME'), CACHE_SUBDIR)
        out_dir.mkdir(parents=True)
        self.out_dir = out_dir
    
    @component.output_types(paths=List[Path])
    def run(self, bstreams: List[ByteStream]):
        paths=[]
        for bstream in bstreams:
            url = bstream.meta['url']
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename:  # Handle cases where there's no filename in the URL
                raise ValueError("Missing base name in {url}")
            filepath = os.path.join(self.out_dir, filename)
            # Write the ByteStream content to the file
            bstream.to_file(filepath)
            paths.append(filepath)
        return {paths: paths}
    
    
# @component
# class UnstructuredConverter(UnstructuredFileConverter):

#     def __init__(self, 
#                 api_url: str = UNSTRUCTURED_HOSTED_API_URL,
#                 api_key: Optional[Secret] = Secret.from_env_var("UNSTRUCTURED_API_KEY", strict=False),
#                 document_creation_mode: Literal[
#                     "one-doc-per-file", "one-doc-per-page", "one-doc-per-element"
#                 ] = "one-doc-per-file",
#                 separator: str = "\n\n",
#                 unstructured_kwargs: Optional[Dict[str, Any]] = None,
#                 progress_bar: bool = True,
#                  **kwargs):
#         super().__init__(api_url=api_url, api_key=api_key, document_creation_mode=document_creation_mode,
#                         separator=separator, unstructured_kwargs=unstructured_kwargs,
#                         progress_bar=progress_bar,
#                         **kwargs)
#         self.cache_dir = os.path.join(os.getenv("HOME"), '.cache/haystack')
#         os.mkdir(self.cache_dir)