from typing_extensions import Literal

from pydantic import BaseModel, Field, ConfigDict
from langgraph.graph import MessagesState
from open_browser.utils.bookmark import BookmarksChrome, Folder, Url

class RouteRequest(BaseModel):
    categories: Literal["specific", "youtube", "bookmarks"] = Field(
        description="Decide what kind of url should open"
    )
    
    
class WebBrowser(MessagesState):    
    categories_url: str
    specific_url: Url | None
    youtube_search: list[str]
    bookmark_folder: Folder | None


class Youtube(BaseModel):
    youtube_search: list[str] = Field(
        description="List with tags for search in youtube"
    )
    

class SpecificUrl(BaseModel):
    name: str = Field(
        description="Specific url name from user`s list that user want to open"
    )


class Bookmarks(BaseModel):
    folder_id: int | None = Field(
        description="Index of parent bookmarks folder where should search children folder and url"
    )
    folder_name: str = Field(
        description="Name of children folder with url"
    )

