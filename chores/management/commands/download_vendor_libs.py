import base64
import hashlib
import urllib.request
from pathlib import Path
from typing import Any, Optional

from django.core.management.base import BaseCommand

LIBS = [
    dict(
        filename="htmx.min.js",
        url="https://unpkg.com/htmx.org@1.9.2",
        hash="sha384-L6OqL9pRWyyFU3+/bjdSri+iIphTN/bvYyM37tICVyOJkWZLpP2vGn6VUEXgzg6h"
    ),
]


def hash(alg, data):
    hasher = hashlib.new(alg)
    hasher.update(data)
    return base64.b64encode(hasher.digest()).decode()


class Command(BaseCommand):
    help = "Download vedor libraries"

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        vendor_path = (Path(__file__).resolve().parent.parent.parent /
                       "static" / "chores" / "js" / "vendor")

        if not vendor_path.exists():
            vendor_path.mkdir(parents=True)

        for lib in LIBS:
            hash_parts = lib["hash"].split("-", 1)

            lib_file_path = vendor_path / lib["filename"]
            if lib_file_path.exists():
                lib_file_contents = lib_file_path.read_bytes()
                file_hash = hash(hash_parts[0], lib_file_contents)
                if file_hash == hash_parts[1]:
                    print(
                        f"[{lib['filename']}] Local file exists and hash matches")
                    continue

                print(f"[{lib['filename']}] Local hash mismatch")

            with urllib.request.urlopen(lib["url"]) as resp:
                data = resp.read()

                data_hash = hash(hash_parts[0], data)
                if data_hash != hash_parts[1]:
                    print(f"[{lib['filename']}] Download hash mismatch")

                lib_file_path.write_bytes(data)
                print(f"[{lib['filename']}] File downloaded")
