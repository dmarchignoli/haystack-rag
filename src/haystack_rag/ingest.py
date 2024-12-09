#!/bin/env python3

import os
from haystack.components.fetchers import LinkContentFetcher

BASE_DIR='.'

def load_library_urls():
    with open(os.path.join(BASE_DIR, 'resources/library_urls.txt')) as f:
        return [x.strip() for x in f.readlines()]

print(load_library_urls())

fetcher = LinkContentFetcher()

library_docs = fetcher.run(urls=load_library_urls())
#print(result)
