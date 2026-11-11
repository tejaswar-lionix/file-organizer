#!/usr/bin/env python3
"""Sort files into category folders by extension."""
import os
import shutil

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp"},
    "Documents": {".pdf", ".docx", ".txt", ".md"},
    "Audio": {".mp3", ".wav", ".flac"},
    "Video": {".mp4", ".mkv", ".mov"},
    "Archives": {".zip", ".tar", ".gz"},
}


def category_for(filename, mapping=None):
    mapping = mapping or CATEGORIES
    extension = os.path.splitext(filename)[1].lower()
    for category, extensions in mapping.items():
        if extension in extensions:
            return category
    return "Other"


def plan_organize(filenames, mapping=None):
    return [(name, category_for(name, mapping)) for name in filenames]


def organize(directory, dry_run=True, mapping=None):
    moved = []
    for name in sorted(os.listdir(directory)):
        source = os.path.join(directory, name)
        if not os.path.isfile(source):
            continue
        category = category_for(name, mapping)
        destination_dir = os.path.join(directory, category)
        destination = os.path.join(destination_dir, name)
        if not dry_run:
            os.makedirs(destination_dir, exist_ok=True)
            shutil.move(source, destination)
        moved.append((name, category))
    return moved


def load_mapping(path):
    """Load a JSON extension map formatted as {"Category": [".ext"]}."""
    import json

    with open(path, encoding="utf-8") as handle:
        raw = json.load(handle)
    return {
        category: {ext.lower() for ext in extensions}
        for category, extensions in raw.items()
    }
