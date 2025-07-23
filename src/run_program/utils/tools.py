import os

FOLDER_PATH = os.path.join(os.environ["APPDATA"], "Microsoft", "Internet Explorer", "Quick Launch", "User Pinned", "TaskBar")

def find_shortcut():
    """Find all shortcut that pinned in task bar"""

    folder = os.walk(FOLDER_PATH)
    for _, _, files in folder:
        yield from (name for name in files if name.endswith(".lnk"))

def run_program(name):
    """Start program"""

    path = os.path.join(FOLDER_PATH, name)
    os.startfile(path)