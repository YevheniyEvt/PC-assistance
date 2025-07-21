import time
import os
import requests
import webbrowser
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage

from open_browser.utils.state import WebBrowser, RouteRequest, SpecificUrl, Youtube, Bookmarks
from open_browser.utils.prompt import ROUTE_REQUEST_PROMPT, CHOSE_SPECIFIC_URL, CREATE_SEARCH_FOR_YOUTUBE_PROMPT, FIND_FOLDER_NAME_PROMPT
from open_browser.utils.tools import read_bookmark_file
from open_browser.utils.bookmark import BookmarksChrome, Folder, Url


MY_URL = {"myplatform": "http://127.0.0.1:7900/", "friends": "https://druzi-hdrezka.net/238-subtitles/"}
MY_URL_NEW = [Url({"name": "myplatform", "url": "http://127.0.0.1:7900/"}), Url({"name": "friends", "url": "https://druzi-hdrezka.net/238-subtitles/"})]
MY_URL_FOLDER = Folder({"children": MY_URL_NEW})

LOCAL_HOST = "http://127.0.0.1"
PATH_SCRIPT_RUN_LOCAL_HOST = "C:\\MyProects\\scripts\\autorunserver7900.bat"

YOUTUBE_URL_NEW = Url({"name": "youtube", "url": "https://www.youtube.com/"})
BOOKMARK_FOLDER_LOOKING_FOR = "Education"
CHROME_BOOKMARK_FILE_PATH = os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data", "Default", "Bookmarks")

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")


def categorize_request(state: WebBrowser) -> WebBrowser:
    """Categorize what kind of url user want to see."""

    sys_msg = SystemMessage(content=ROUTE_REQUEST_PROMPT.format(my_url_list=[url.name for url in MY_URL_NEW]))
    human_msg = state["messages"][-1]
    decision = llm.with_structured_output(RouteRequest).invoke([sys_msg, human_msg])
    return {"categories_url": decision.categories}

def route_decision(state: WebBrowser) -> str:
    """Route next step """
    if state["categories_url"] == "specific":
        return "get specific url"
    elif state["categories_url"] == "youtube":
        return "create youtube search"
    elif state["categories_url"] == "bookmarks":
        return "get bookmarks url"
    
def get_specific_url(state: WebBrowser) ->WebBrowser:
    """Chose specific url from user's list of urls"""

    urls_name = [url.name for url in MY_URL_FOLDER.get_urls(links=False)]

    sys_msg = SystemMessage(content=CHOSE_SPECIFIC_URL.format(my_url_list=urls_name))
    human_msg = state["messages"][-1]
    decision = llm.with_structured_output(SpecificUrl).invoke([sys_msg, human_msg])
    url = MY_URL_FOLDER.get(decision.name)

    if url is None:
        ai_msg = f"Can't open, please specify your request. I looking for {decision.name} is it correct"
        return {"messages": AIMessage(content=ai_msg), "specific_url": None}
    else:
        return {"specific_url": url}
    
def specific_url_exist(state: WebBrowser) ->str:
    """If chosen name correct open url if not go to END"""

    if state["specific_url"] is None:
        return "url not exist"
    else:
        return "url exist"
    
def open_specific_url(state: WebBrowser) -> WebBrowser:
    """Open specific url from user`s list in browser"""

    url: Url = state["specific_url"]

    if not url.curl():
        if url.url.startswith(LOCAL_HOST):
            os.startfile(PATH_SCRIPT_RUN_LOCAL_HOST)
            time.sleep(3)
        else:
            ai_msg = AIMessage(content=f"Your url: {url.url} doesn't work, check it")
            return {"messages": [ai_msg]}
    url.open_new()
    
    
def create_youtube_search(state: WebBrowser) -> WebBrowser:
    """Create tags for searching in youtube from user's request"""

    sys_msg = SystemMessage(content=CREATE_SEARCH_FOR_YOUTUBE_PROMPT)
    human_msg = state["messages"][-1]
    decision = llm.with_structured_output(Youtube).invoke([sys_msg, human_msg])
    return {"youtube_search": decision.youtube_search}

def open_youtube(state: WebBrowser):
    """Open youtube url in browser"""
    youtube_url: Url = YOUTUBE_URL_NEW
    search = "results?search_query=" + "+".join(state["youtube_search"])
    if youtube_url.url[-1] != "/":
        youtube_url.url += f"/{search}"
    else:
        youtube_url.url += search
    youtube_url.open_new()

def get_bookmarks_url(state: WebBrowser) ->WebBrowser:
    """Find urls in bookmark folders"""
    try:
        bookmark = BookmarksChrome()
    except FileNotFoundError:
        return {"messages": AIMessage(content=f"Sorry, file: {bookmark.path}  does not exist"), "bookmark_folder": None}

    
    folders = bookmark.folders()
    folders_name = [folder.name for folder in folders]
    sys_msg = SystemMessage(content=FIND_FOLDER_NAME_PROMPT.format(child_folders=folders_name))
    human_msg = state["messages"][-1]
    decision = llm.with_structured_output(Bookmarks).invoke([sys_msg, human_msg])
    folder_with_url = None
    for folder in folders:
            if folder.name.lower() == decision.folder_name.lower():
                folder_with_url = folder
   
    if decision.folder_id is None or folder_with_url is None:
        ai_msg = f"Sorry, folder or url: {decision.folder_name}  does not exist. Are you sure is it you are looking for?"
        return {"messages": AIMessage(content=ai_msg), "bookmark_folder": folder_with_url}
    else:
        return {"bookmark_folder": folder_with_url}


def bookmark_folder_exist(state: WebBrowser) ->str:
    """If chosen name of folder correct - open url from it,
        if not - go to END"""
    
    if state["bookmark_folder"] is not None:
        return "bookmark exist"
    else:
        return "bookmark not exist"

def open_from_bookmarks(state: WebBrowser):
    """Open url in browser"""
    if isinstance(state["bookmark_folder"], Folder):
        state["bookmark_folder"].open_urls()
        

