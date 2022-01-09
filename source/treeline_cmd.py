#!/usr/bin/env python3
"""TreeLine Command-line tool

        Arguments:
            command -- export or cpfmt
            parameters -- command parameters

        Examples:
            treeline_cmd export source.trln dest_file.tex
            treeline_cmd cpfmt format.trln source.trln dest.trln
            treeline_cmd mergefmt struct.trln view.trln dest.trln
"""
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
    if len(sys.argv) <= 1:
        help(sys.modules['__main__'])
        sys.exit(-1)

    cmd = sys.argv[1]

    available_cmds = ['export', 'cpfmt', 'mergefmt']
    if not cmd in available_cmds:
        raise ValueError(f"invalid command: {cmd}. available commands: {available_cmds}")

    params = sys.argv[2:]
    
    builtins._ = markNoTranslate
    builtins.N_ = markNoTranslate

    print("treeline command-line tools.")
    if cmd == 'export':
        cmd_export(params)
        
    if cmd == 'cpfmt':
        cmd_cpfmt(params)

    if cmd == 'mergefmt':
        cmd_mergefmt(params)
