import os
from typing import Optional
from haystack import component
from haystack.dataclasses import ByteStream
from pathlib import Path
from .utils import url_basename

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
    
    @component.output_types(paths=list[Path])
    def run(self, streams: list[ByteStream]) -> dict[str, list[Path]]:
        paths=[]
        for bstream in streams:
            filename = url_basename(bstream.meta['url'])
            filepath = self._out_dir.joinpath(filename)
            # Write the ByteStream content to the file
            bstream.to_file(filepath)
            paths.append(filepath)
        return {'paths': paths}
