import json
import os
from pathlib import Path


def ensure_dir(file_path: str) -> None:
	Path(os.path.dirname(file_path)).mkdir(parents=True, exist_ok=True)


def read_json(file_path: str, fallback=None):
	try:
		with open(file_path, 'r', encoding='utf-8') as f:
			return json.load(f)
	except FileNotFoundError:
		return fallback


def write_json(file_path: str, data):
	ensure_dir(file_path)
	with open(file_path, 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
	return data


def push_json_array(file_path: str, item):
	arr = read_json(file_path, []) or []
	arr.append(item)
	write_json(file_path, arr)
	return arr


def upsert_by_key(file_path: str, key: str, item: dict):
	lst = read_json(file_path, []) or []
	idx = next((i for i, x in enumerate(lst) if x.get(key) == item.get(key)), -1)
	if idx >= 0:
		lst[idx] = { **lst[idx], **item }
	else:
		lst.append(item)
	write_json(file_path, lst)
	return item
