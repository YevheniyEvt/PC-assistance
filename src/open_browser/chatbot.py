from langgraph.graph import StateGraph, START, END

from open_browser.utils.state import WebBrowser
from open_browser.utils.nodes import (categorize_request, route_decision,
                                      get_specific_url, open_specific_url, specific_url_exist,
                                      create_youtube_search, open_youtube,
                                      get_bookmarks_url, open_from_bookmarks, bookmark_folder_exist
                                      
                                      )

router_builder = StateGraph(WebBrowser)


router_builder.add_node("categorize request", categorize_request)

router_builder.add_node("get specific url", get_specific_url)
router_builder.add_node("open specific url", open_specific_url)
router_builder.add_node("open youtube", open_youtube)
router_builder.add_node("open url from bookmarks", open_from_bookmarks)
router_builder.add_node("create youtube search", create_youtube_search)
router_builder.add_node("get bookmarks url", get_bookmarks_url)
router_builder.add_edge(START, "categorize request")
router_builder.add_conditional_edges(
    "categorize request",
    route_decision,
    {
        "get specific url": "get specific url",
        "create youtube search": "create youtube search",
        "get bookmarks url": "get bookmarks url"
    },
)
router_builder.add_conditional_edges(
    "get bookmarks url",
    bookmark_folder_exist,
    {"bookmark exist": "open url from bookmarks", "bookmark not exist": END}
)
router_builder.add_conditional_edges(
    "get specific url",
    specific_url_exist,
    {"url exist": "open specific url", "url not exist": END}
)
router_builder.add_edge("create youtube search", "open youtube")
router_builder.add_edge("get specific url", "open specific url")
router_builder.add_edge("open specific url", END)
router_builder.add_edge("open youtube", END)
router_builder.add_edge("open url from bookmarks", END)

graph = router_builder.compile()