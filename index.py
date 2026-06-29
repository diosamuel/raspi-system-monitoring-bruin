import json
import os
import time

from pipeline.ingest import ingest

JSONL_PATH = os.path.join(os.path.dirname(__file__), "metrics.jsonl")

while True:
    line = ingest()
    with open(JSONL_PATH, "a") as f:
        f.write(line + "\n")
    print(line)
    time.sleep(1)
