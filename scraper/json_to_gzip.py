import os
import json
import gzip
import shutil

with open('data/matches_5146330922-5148330922_INCOMPLETE.json', 'rb') as f_in:
    with gzip.open('data/matches_5148330922-5148330922.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


