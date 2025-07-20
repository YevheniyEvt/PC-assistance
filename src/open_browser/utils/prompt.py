ROUTE_REQUEST_PROMPT = """
You should categorize what kind of url user want to see.
1.  Route the input to specific only if user want open some url from this list: {my_url_list}.
2. Route the input to youtube if user want open YouTube or find something in YouTube or to see some video.
3. Route the input to bookmarks in all other cases. 
"""
CHOSE_SPECIFIC_URL = """
You have list with user's url name: {my_url_list}.
1. Analyze user's request and chose from this list {my_url_list} name that user want to open then return chosen name.
"""

CREATE_SEARCH_FOR_YOUTUBE_PROMPT = """
You should create search request for youtube.
1. Analyze step by step user's request.
2. Split that request for tags that can be useful for search in youtube url.
    Example: 'https://www.youtube.com/results?search_query=langgraph+agent+project). Un this example - langgraph, agent, project 
    is tag for search in youtube.
3. Use only words that convey the main meaning of user's request for watching.
"""
FIND_FOLDER_NAME_PROMPT = """
You have a list with folders from Chrome browser: {child_folders}.
You should:
1. Analyze user's request and find in {child_folders} name of folder that user want to open and return that name and id. Start from 0.
    Be sure that {child_folders}[id] == name.
2. If there are no such folder name in {child_folders} return id = None and folder name that you looking for.

"""
