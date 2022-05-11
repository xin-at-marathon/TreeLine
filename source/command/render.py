#!/usr/bin/env python3
import os.path
import json
from pathlib import Path
from .shared import merge_formats
from .node_format_ext import *

AVAILABLE_NODE_TYPES = ['topic', 'book', 'article']
AVAILABLE_OUTPUT_TYPES = ['document']

def cmd_render(params):
    node_type = params[0]
    if not node_type in AVAILABLE_NODE_TYPES:
        raise ValueError(f"invalid node type: {node_type}. available types: {AVAILABLE_NODE_TYPES}")

    output_type = params[1]
    if not output_type in AVAILABLE_OUTPUT_TYPES:
        raise ValueError(f"invalid output type: {output_type}. available types: {AVAILABLE_OUTPUT_TYPES}")

    output_suffix = params[2]
    repo_file = os.path.abspath(params[3])
    output_dir = params[4]

    template_formats = get_template_formats(node_type, output_type, output_suffix)
     
    print(f"command: [render] tree nodes via template")
    print(f"node type: {node_type}")
    print(f"output type: {output_type}")
    print(f"output suffix: {output_suffix}")
    print(f"repo: {repo_file}")
    print(f"template formats: {len(template_formats)}")
    print(f"output dir: {output_dir}")

    repo_path = Path(repo_file)

    with repo_path.open('r', encoding='utf-8') as repo_handler:
        # merge the repo with formats
        repo_json = json.load(repo_handler)
        merged_formats = merge_formats(repo_json["formats"], template_formats)
        repo_json["formats"] = merged_formats

        # locate the root_stpos of the node type
        import treestructure
        repo_struct = treestructure.TreeStructure(repo_json)
        root_spots = repo_struct.rootSpots()
        selected_root_spot = None
        for spot in root_spots:
            if spot.nodeRef.data['Name'] == node_type:
                selected_root_spot = spot
                break

        if not selected_root_spot:
            raise Exception(f"Can't find node type: {node_type}")

        
        # iterate each child and render
        for child_node in selected_root_spot.nodeRef.childList:
            dst_dir = output_dir.replace('uid', child_node.uId)
            Path(dst_dir).mkdir(parents=True, exist_ok=True)
            dst_file = f"{dst_dir}/index.{output_suffix}"

            # get output lines
            lines = format_output_ext(child_node, False, False)
            # replace node id placeholders
            lines = map(lambda line: line.replace('#{id}', child_node.uId), lines)

            # write to file    
            dst_path = Path(dst_file)
            with dst_path.open('w', encoding='utf-8') as dst_handler:
                dst_handler.writelines(lines)
    
            print(f"output done. file: {dst_file}")
    

def get_template_formats(node_type, output_type, output_suffix):
    template_path = Path(f"/input/template/{node_type}-{output_type}-{output_suffix}.json")
    template_handler = template_path.open('r', encoding='utf-8')
    template_json = json.load(template_handler)

    formats = template_json["formats"]
    # also load topic formats for article, book, etc..
    if node_type != 'topic':
        topic_formats = get_template_formats('topic', output_type, output_suffix)
        formats.extend(topic_formats)

    return formats
