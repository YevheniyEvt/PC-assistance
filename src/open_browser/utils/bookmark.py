import os
import sys
import pathlib
import json
import datetime
import webbrowser
import requests
from abc import ABC, abstractmethod


class ChildrenBase(ABC):

    def __init__(
            self,
            data: dict,
            strftime: str = "%B %Y %H:%M:%S %Z"
            ):
        self.strftime = strftime
        for key, value in data.items():
            self.__setattr__(key, value)

    def _date_time(self, time: int) ->str:
        seconds, micros = divmod(time, 1000000)
        days, seconds = divmod(seconds, 86400)
        return (datetime.datetime(1601, 1, 1) + datetime.timedelta(days, seconds, micros)).strftime(self.strftime) 

    def __setattr__(self, name, value):
        if "date" in name:
            value = self._date_time(int(value))
        return super().__setattr__(name, value)
    

class Url(ChildrenBase):
    """Info about url from bookmarks"""

    def __repr__(self):
        return f"Url(name: {self.name}, url: {self.url})"
    
    def __str__(self):
        return self.url
    
    def open(self, new: int=0) ->bool:
        """Open url in default browser
        If opening the browser succeeds, return True.
        If there is a problem, return False."""

        return webbrowser.open(self.url, new=new)
        
    def open_new(self) ->bool:
        """Open url in a new window of the default browser.
        If not possible, then open url in the only browser window.
        """

        return self.open(new=1)
        
    def open_new_tab(self) ->bool:
        """Open url in a new page ("tab") of the default browser.
        If not possible, then the behavior becomes equivalent to open_new().
        """

        return self.open(new=2)
    
    def curl(self):
        return requests.get(url=self.url)


class Folder(ChildrenBase):
    """Info about folder from bookmarks.
        If want create new folder:
        pass dict with key 'children' that will be attribute and value that will be value of attribute
        Example:
            >> folder = Folder({"children": "some_val"})
            >> folder.children
            >> some_val
            """

    def __init__(self, data, strftime="%B %Y %H:%M:%S %Z"):
        super().__init__(data, strftime)
        if hasattr(self, "children"):
            try:
                self.children = [Folder(child) if child["type"] == "folder" else Url(child) for child in self.children]
            except TypeError:
                pass

    def __iter__(self):
        for child in self.children:
            yield child

    def __len__(self):
        return len(self.children)
    
    def __getitem__(self, position):
        return self.children[position]
    
    def __contains__(self, value):
        return value in self.children
    
    def __repr__(self):
        return f"Folder(name: {self.name})"
    
    def __str__(self):
        return self.name
    
    def get_urls(self, links: bool=False):
        """All urls in current folder.
        If links = True list with links
        if links = False list with instance Url"""

        return [child.url if links else child for child in self if isinstance(child, Url)]

    def get_folders(self):
        """All folders in current folder"""

        return [child for child in self if isinstance(child, self.__class__)]
    
    def get(self, name: str) ->ChildrenBase | None:
        """Folder or Url with name from current folder"""

        for child in self:
            if child.name.lower() == name.lower():
                return child
            
    def open_urls(self):
        """Open urls from folder in default browser"""
        
        for url in self.get_urls():
            url.open()


class BookmarksABC(ABC):
    """Abstract class for specifik bookmark's classes"""
    
    @property
    @abstractmethod
    def bookmarks_file_path(self) -> str:
        """Check what kind of platform is and set  return bookmarks file path for
        specific browser. It is should be property"""


class BookmarksBase:
    """Base class for bookmark. Don't use it"""
    
    def __init__(
            self,
            path: str | None = None
            ):
        
        if path is not None:
            self.bookmarks_file_path = path
    
    def _load_file(self)-> dict:
        if self.exist():
            with open(self.bookmarks_file_path, 'r', encoding='utf-8') as file:
                return json.load(file)["roots"]["bookmark_bar"]
        else:
            raise FileNotFoundError(f"Can't find file: {self._file_path}")   
        
    @property
    def path(self) ->str:
        """Path where bookmarks file is"""

        return self.bookmarks_file_path
    
    @property
    def bookmark_bar(self) ->Folder:
        """Main folder of bookmark bar"""

        return Folder(self._load_file())
    
    def exist(self) -> bool:
        return pathlib.Path(self.bookmarks_file_path).exists()
    
    def folders(self, folders: Folder | None = None) ->list[Folder]:
        """All folders that is in bookmark bar"""

        all_folders = []
        if folders is None:
            folders = self.bookmark_bar.get_folders()
        for folder in folders:
            all_folders += self.folders(folder.get_folders())
            all_folders.append(folder)
        return all_folders
    

class BookmarksChrome(BookmarksABC, BookmarksBase):
    """Open Chrome browser bookmarks"""
    
    @property
    def bookmarks_file_path(self) ->str:
        if sys.platform[:3] == "win":
            bookmarks_file_path = os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data", "Default", "Bookmarks")
            return bookmarks_file_path


class Bookmarks(BookmarksBase):
    """If have bookmark file pass the path to it.

    If want use standart browser path you need to pass the browser name.
    Implemented only for Chrome"""
    
    def __new__(
            cls,
            browser: str | None = None,
            path: str |None = None
            ):
        
        if path is not None:
            return super().__new__(cls)

        if browser.lower() == 'chrome':
            return BookmarksChrome()