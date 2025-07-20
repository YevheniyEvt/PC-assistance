import pathlib
import json


def read_bookmark_file(path: str, folder_name: str) -> tuple:
    """Open file with Chrome bookmarks return list of urls"""

    if pathlib.Path(path).exists():
        with open(path, 'r', encoding='utf-8') as file:
            file_from_json = json.load(file)
            parent_folders = file_from_json["roots"]["bookmark_bar"]["children"]
            for folder in parent_folders:
                 if folder["name"] == folder_name:
                    folders = [child for child in folder.get("children", []) if folder["type"] == "folder"]
                    folders_name = [child["name"] for child in folder.get("children", []) if folder["type"] == "folder"]
                    return folders, folders_name
    else:
        return ([],[])

