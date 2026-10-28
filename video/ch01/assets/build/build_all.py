# -*- coding: utf-8 -*-
"""Orchestrate ch01 long lecture build."""
import subprocess, sys
from pathlib import Path
BUILD = Path(__file__).resolve().parent

def run(script):
    print("=" * 60, script)
    r = subprocess.call([sys.executable, str(BUILD / script)])
    if r != 0:
        raise SystemExit(r)

if __name__ == "__main__":
    run("parse_script.py")
    run("render_slides.py")
    run("render_vo.py")
    run("render_cover.py")
    run("assemble.py")
    print("ALL DONE")
