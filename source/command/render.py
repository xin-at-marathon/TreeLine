#!/usr/bin/env python3
import os.path
import json
from pathlib import Path
from .shared import merge_formats
import shutil 

def cmd_render(params):
    node_type = params[0] # topic/book/article/...
    available_types = ['topic', 'book', 'article']
    if not node_type in available_types:
        raise ValueError(f"invalid node type: {node_type}. available types: {available_types}")
    
    repo_file = os.path.abspath(params[1])
    res_dir = os.path.abspath(params[2])
    template_file = os.path.abspath(params[3])
    output_dir = params[4]
    
    print(f"command: render tree nodes via template[render]")
    print(f"node type: {node_type}")
    print(f"repo: {repo_file}")
    print(f"resource dir: {res_dir}")
    print(f"template: {template_file}")
    print(f"output dir: {output_dir}")

    repo_path = Path(repo_file)
    template_path = Path(template_file)

    import treestructure
    template_handler = template_path.open('r', encoding='utf-8')
    template_json = json.load(template_handler)

    with repo_path.open('r', encoding='utf-8') as repo_handler:
        repo_json = json.load(repo_handler)
        merged_formats = merge_formats(repo_json["formats"], template_json["formats"])
        repo_json["formats"] = merged_formats

        repo_struct = treestructure.TreeStructure(repo_json)
        root_spots = repo_struct.rootSpots()

        selected_root_spot = None
        for spot in root_spots:
            if spot.nodeRef.data['Name'] == node_type:
                selected_root_spot = spot
                break

        if not selected_root_spot:
            raise Exception(f"Can't find node type: {node_type}")


        for child_node in selected_root_spot.nodeRef.childList:
            lines = child_node.outputEx(False, False)
            dst_dir = output_dir.replace('uid', child_node.uId)

            Path(dst_dir).mkdir(parents=True, exist_ok=True)
            shutil.rmtree(dst_dir, ignore_errors=True)

            # copy res directories
            src_res_dir = f"{res_dir}/{node_type}/{child_node.uId}"
            shutil.copytree(src_res_dir, dst_dir)
                
#            Path(dst_dir).mkdir(parents=True, exist_ok=True)
            dst_path = Path(f"{dst_dir}/index.html")
            with dst_path.open('w', encoding='utf-8') as dst_handler:
                dst_handler.writelines(lines)

            
    
