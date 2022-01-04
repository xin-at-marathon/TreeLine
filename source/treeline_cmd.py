#!/usr/bin/env python3
import sys
import builtins
from command import *

def markNoTranslate(text, comment=''):
    """Dummy translation function, only used to mark text.

        Arguments:
            text -- the text to be translated
            comment -- a comment used only as a guide for translators
    """
    return text


if __name__ == '__main__':
    """TreeLine Command-line tool

        Arguments:
            command -- export or cpfmt
            parameters -- command parameters

        Examples:
            treeline_cmd export source.trln dest_file.tex
            treeline_cmd cpfmt format.trln source.trln dest.trln
    """
    cmd = sys.argv[1]
    available_cmds = ['export', 'cpfmt']
    if not cmd in available_cmds:
        raise ValueError(f"invalid command: {cmd}")

    params = sys.argv[2:]
    
    builtins._ = markNoTranslate
    builtins.N_ = markNoTranslate

    print("treeline command-line tools.")
    if cmd == 'export':
        cmd_export(params)
        
    if cmd == 'cpfmt':
        cmd_cpfmt(params)
        
