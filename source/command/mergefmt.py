#!/usr/bin/env python3
import pathlib
import os.path
import json

from .shared import merge_formats


def cmd_mergefmt(params):
    struct_file = os.path.abspath(params[0])
    view_file = os.path.abspath(params[1])
    dst_file = os.path.abspath(params[2])

    print(f"command:\tmerge format[mergefmt]")
    print(f"\nstruct:\t\t{struct_file}\nview:\t\t{view_file}\ndest:\t\t{dst_file}")

    struct_path = pathlib.Path(struct_file)
    view_path = pathlib.Path(view_file)
    dst_path = pathlib.Path(dst_file)

    with struct_path.open('r', encoding='utf-8') as struct_handler:
        struct_json = json.load(struct_handler)

        with view_path.open('r', encoding='utf-8') as view_handler:
            view_json = json.load(view_handler)

            merged_formats = merge_formats(struct_json["formats"], view_json["formats"])

            view_json["formats"] = merged_formats
            
            with dst_path.open('w', encoding='utf-8') as dst_handler:
                json.dump(view_json, dst_handler, ensure_ascii=False, indent=4)
