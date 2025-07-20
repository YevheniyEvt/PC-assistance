import time
import os
import requests
import webbrowser

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage

from open_browser.utils.state import WebBrowser, RouteRequest, SpecificUrl, Youtube, Bookmarks
from open_browser.utils.prompt import ROUTE_REQUEST_PROMPT, CHOSE_SPECIFIC_URL, CREATE_SEARCH_FOR_YOUTUBE_PROMPT, FIND_FOLDER_NAME_PROMPT
from open_browser.utils.tools import read_bookmark_file


MY_URL = {"myplatform": "http://127.0.0.1:7900/", "friends": "https://druzi-hdrezka.net/238-subtitles/"}
LOCAL_HOST = "http://127.0.0.1"
PATH_SCRIPT_RUN_MYPLATFORM = "C:\\MyProects\\scripts\\autorunserver7900.bat"

YOUTUBE_URL = "https://www.youtube.com/"
BOOKMARK_FOLDER_LOOKING_FOR = "Education"
CHROME_BOOKMARK_FILE_PATH = os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data", "Default", "Bookmarks")

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

def categorize_request(state: WebBrowser) -> WebBrowser:
    """Categorize what kind of url user want to see."""

    sys_msg = SystemMessage(content=ROUTE_REQUEST_PROMPT.format(my_url_list=list(MY_URL.keys())))
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
    
def get_specific_url(state: WebBrowser):
    """Chose specific url from user's list of urls"""

    urls_name = list(MY_URL.keys())

    sys_msg = SystemMessage(content=CHOSE_SPECIFIC_URL.format(my_url_list=urls_name))
    human_msg = state["messages"][-1]
    decision = llm.with_structured_output(SpecificUrl).invoke([sys_msg, human_msg])

    if decision.name not in urls_name:
        ai_msg = "Can't understand, please specify your request."
        return {"messages": AIMessage(content=ai_msg), "specific_url_name": decision.name}
    else:
        return {"specific_url_name": decision.name}
    
def specific_url_exist(state: WebBrowser) ->str:
    """If chosen name correct open url if not go to END"""

    if MY_URL.get(state["specific_url_name"]) is None:
        return "url not exist"
    else:
        return "url exist"
    
def open_specific_url(state: WebBrowser):
    """Open specific url from user`s list in browser"""

    url = MY_URL.get(state["specific_url_name"])
    try:
        requests.get(url=url)
    except ConnectionError:
        if url.startswith(LOCAL_HOST):
            os.startfile(PATH_SCRIPT_RUN_MYPLATFORM)
            time.sleep(3)
        else:
            ai_msg = AIMessage(content=f"Your url: {url} doesn't work, check it")
            return {"messages": [ai_msg]}
    finally:
        webbrowser.open_new(url=url)
    
def create_youtube_search(state: WebBrowser) -> WebBrowser:
    """Create tags for searching in youtube from user's request"""

    sys_msg = SystemMessage(content=CREATE_SEARCH_FOR_YOUTUBE_PROMPT)
    human_msg = state["messages"][-1]
    decision = llm.with_structured_output(Youtube).invoke([sys_msg, human_msg])
    return {"youtube_search": decision.youtube_search}

def open_youtube(state: WebBrowser):
    """Open youtube url in browser"""
    
    if YOUTUBE_URL[-1] != "/":
        url = YOUTUBE_URL + "/"
    else:
        url = YOUTUBE_URL
    search = "results?search_query=" + "+".join(state["youtube_search"])
    webbrowser.open_new(url=url+search)

def get_bookmarks_url(state: WebBrowser):
    """Find urls in bookmark folders"""

    education_folders, education_folders_name = read_bookmark_file(path=CHROME_BOOKMARK_FILE_PATH, folder_name=BOOKMARK_FOLDER_LOOKING_FOR)

    if len(education_folders) == 0:
        return {"messages": AIMessage(content=f"Sorry, file: {CHROME_BOOKMARK_FILE_PATH}  does not exist"), "bookmark_urls": []}

    sys_msg = SystemMessage(content=FIND_FOLDER_NAME_PROMPT.format(child_folders=education_folders_name))
    human_msg = state["messages"][-1]
    decision = llm.with_structured_output(Bookmarks).invoke([sys_msg, human_msg])

    if decision.folder_id is None:
        ai_msg = f"Sorry, folder or url: {decision.folder_name}  does not exist. Are you sure is it you are looking for?"
        return {"messages": AIMessage(content=ai_msg), "bookmark_urls": []}
    else:
        folder_with_url = education_folders[decision.folder_id]["children"]
        urls = [link.get("url") for link in folder_with_url if link.get("type") == "url"]
        return {"bookmark_urls": urls}


def bookmark_folder_exist(state: WebBrowser) ->str:
    """If chosen name of folder correct - open url from it,
        if not - go to END"""
    
    if len(state["bookmark_urls"]) != 0:
        return "bookmark exist"
    else:
        return "bookmark not exist"

def open_from_bookmarks(state: WebBrowser):
    """Open url in browser"""
    
    for url in state["bookmark_urls"]:
        webbrowser.open_new(url=url)

