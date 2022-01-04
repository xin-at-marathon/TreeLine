#!/usr/bin/env python3
import pathlib
import os.path
import json

def cmd_export(params):
    src_file = os.path.abspath(params[0])
    dst_file = os.path.abspath(params[1])

    print(f"command:\texport")
    print(f"\nsource:\t\t{src_file}\ndest:\t\t{dst_file}")

    src_path = pathlib.Path(src_file)
    dst_path = pathlib.Path(dst_file)
    
    import treestructure
    with src_path.open('r', encoding='utf-8') as src_handler:
        src_json = json.load(src_handler)
        src_struct = treestructure.TreeStructure(src_json)
        root_spots = src_struct.rootSpots()
        
        lines = []

        for spot in root_spots:
            lines.extend(spot.nodeRef.outputEx(False, False))
            if spot.nodeRef.formatRef.spaceBetween:
                lines.append('')

        lines = [(line + '\n') for line in lines]
        
        try:
            with dst_path.open('w', encoding='utf-8') as dst_handler:
                dst_handler.writelines(lines)
        except:
            raise
    
