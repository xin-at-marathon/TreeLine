#!/usr/bin/env python3
import pathlib
import os.path
import json

def __replace_fields(a_formats, b_formats, fields):
    for a in a_formats:
        name = a['formatname']

        found = None
        for b in b_formats:
            if name == b['formatname']:
                found = b
                break
            
        if found:
            for f in fields:
                if f in found:
                    a[f] = found[f]
                else:
                    if f in a:
                        del a[f]
                
    return a_formats
    
def cmd_mergefmt(params):
    struct_file = os.path.abspath(params[0])
    src_file = os.path.abspath(params[1])
    dst_file = os.path.abspath(params[2])

    print(f"command:\tmerge format[mergefmt]")
    print(f"\nstruct:\t\t{struct_file}\nsource:\t\t{src_file}\ndest:\t\t{dst_file}")

    struct_path = pathlib.Path(struct_file)
    src_path = pathlib.Path(src_file)
    dst_path = pathlib.Path(dst_file)

    fields = ["outputlines","spacebetween"]
    with struct_path.open('r', encoding='utf-8') as struct_handler:
        struct_json = json.load(struct_handler)

        with src_path.open('r', encoding='utf-8') as src_handler:
            src_json = json.load(src_handler)

            struct_json["formats"] = __replace_fields(struct_json["formats"], src_json["formats"], fields)

            src_json["formats"] = struct_json["formats"]
            
            with dst_path.open('w', encoding='utf-8') as dst_handler:
                json.dump(src_json, dst_handler, ensure_ascii=False, indent=4)
