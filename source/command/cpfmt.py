#!/usr/bin/env python3
import pathlib
import os.path
import json

def cmd_cpfmt(params):
    template_file = os.path.abspath(params[0])
    src_file = os.path.abspath(params[1])
    dst_file = os.path.abspath(params[2])

    print(f"command:\tcopy format[cpfmt]")
    print(f"\ntemplate:\t{template_file}\nsource:\t\t{src_file}\ndest:\t\t{dst_file}")

    template_path = pathlib.Path(template_file)
    src_path = pathlib.Path(src_file)
    dst_path = pathlib.Path(dst_file)

    with template_path.open('r', encoding='utf-8') as template_handler:
        template_json = json.load(template_handler)

        with src_path.open('r', encoding='utf-8') as src_handler:
            src_json = json.load(src_handler)
            
            src_json["formats"] = template_json["formats"]
            
            with dst_path.open('w', encoding='utf-8') as dst_handler:
                json.dump(src_json, dst_handler, ensure_ascii=False, indent=4)
