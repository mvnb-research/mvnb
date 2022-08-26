from os import makedirs
from pathlib import Path
from shutil import copy
from subprocess import check_call


def build(src, dst):
    gui_proj = f"{src}/mvnb-gui"
    gui_dist = f"{gui_proj}/dist"

    check_call(["yarn", "install"], cwd=gui_proj)
    check_call(["yarn", "parcel", "build"], cwd=gui_proj)

    makedirs(f"{dst}/mvnb/gui", exist_ok=True)
    for path in Path(gui_dist).glob("*.*"):
        copy(path, f"{dst}/mvnb/gui")
