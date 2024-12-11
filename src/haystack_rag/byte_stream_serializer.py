import os
from typing import List, Optional
from haystack import component
from haystack.dataclasses import ByteStream
from pathlib import Path
from urllib.parse import urlparse

CACHE_SUBDIR = '.cache/haystack'

@component
class ByteStreamMaterializer():
    """
    Saves the byte streams in input to filesystem returns the file paths
    """
    def __init__(self, out_dir: Optional[Path] = None):
        home = os.getenv('HOME')
        assert home is not None
        self._out_dir = out_dir if out_dir is not None \
          else Path(home).joinpath(CACHE_SUBDIR)
        if not self._out_dir.exists():
          self._out_dir.mkdir(parents=True)
    
    @component.output_types(paths=List[Path])
    def run(self, streams: List[ByteStream]):
        paths=[]
        for bstream in streams:
            url = bstream.meta['url']
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename:  # Handle cases where there's no filename in the URL
                raise ValueError("Missing base name in {url}")
            filepath = self._out_dir.joinpath(filename)
            # Write the ByteStream content to the file
            bstream.to_file(filepath)
            paths.append(filepath)
        return {'paths': paths}
