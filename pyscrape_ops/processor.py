# pyscrape_ops/processor.py
from typing import List, Dict
import pandas as pd
import hashlib

def normalize_text_field(s: str) -> str:
    if s is None:
        return ""
    return " ".join(s.split())

def fingerprint(item: Dict[str,str]) -> str:
    joined = "|".join([str(item.get(k, "")) for k in sorted(item.keys())])
    return hashlib.md5(joined.encode("utf-8")).hexdigest()

def process_items(items: List[Dict[str,str]], dedupe: bool = True) -> pd.DataFrame:
    if not items:
        return pd.DataFrame()
    for it in items:
        for k, v in list(it.items()):
            it[k] = normalize_text_field(v)
    if dedupe:
        seen = set()
        filtered = []
        for it in items:
            fp = fingerprint(it)
            if fp not in seen:
                seen.add(fp)
                filtered.append(it)
        items = filtered
    df = pd.DataFrame(items)
    return df
