#!/usr/bin/env python3
import sys
import pathlib
import os.path
import builtins
import json

def markNoTranslate(text, comment=''):
    """Dummy translation function, only used to mark text.

        Arguments:
            text -- the text to be translated
            comment -- a comment used only as a guide for translators
    """
    return text


if __name__ == '__main__':
    """Main event loop for TreeLine Command-line tool
    python3 source/cmdline.py [type] [template.trln] [source.trln] [dest_dir]
    type: latex/html
    """
    etype = sys.argv[1]
    if etype == "latex":
        ext = "tex"
    elif etype == "html":
        ext = "html"
    else:
        raise ValueError(f"invalid type: {etype}")
        
    template = os.path.abspath(sys.argv[2])
    source = os.path.abspath(sys.argv[3])
    name = os.path.basename(source).split('.')[0]
    dest_dir = os.path.abspath(sys.argv[4])
    dest = f"{dest_dir}/{name}.{ext}"

    print(f"command-line:\texport")
    print(f"type:\t\t{etype}\ntemplate:\t{template}\nsource:\t\t{source}\ndest:\t\t{dest}")

    pathSource = pathlib.Path(source)
    pathTemplate = pathlib.Path(template)
    pathDest = pathlib.Path(dest)

    builtins._ = markNoTranslate
    builtins.N_ = markNoTranslate
    
    import treestructure
    with pathSource.open('r', encoding='utf-8') as fileSource:
        jsonSource = json.load(fileSource)
        structSource = treestructure.TreeStructure(jsonSource)


        structTemplate = None
        try:
            with pathTemplate.open('r', encoding='utf-8') as fileTemplate:
                jsonTemplate = json.load(fileTemplate)
                structTemplate = treestructure.TreeStructure(jsonTemplate,
                                                           addSpots=False)
        except:
            raise
        if not structTemplate:
            raise Exception("template invalid")

        for nodeFormat in structTemplate.treeFormats.values():
            structSource.treeFormats.addTypeIfMissing(nodeFormat)
            

        rootSpots = structSource.rootSpots()
        
        lines = []

        for spot in rootSpots:
            lines.extend(spot.nodeRef.outputEx(False, False))

        try:
            with pathDest.open('w', encoding='utf-8') as fileDest:
                fileDest.writelines([(line + '\n') for line in lines])
        except:
            raise


