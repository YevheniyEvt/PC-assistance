from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

from developer_chatbot.chatbot import router_builder as developer
from open_browser.chatbot import router_builder as browser
from personal_helper.utils.state import Helper
from personal_helper.utils.nodes import categorize_request, standard_answer, route_decision

router_builder = StateGraph(Helper)

router_builder.add_node("categorize_request", categorize_request)
router_builder.add_node("standard_answer", standard_answer)
router_builder.add_node("browser_helper", browser.compile())
router_builder.add_node("developer_helper", developer.compile())

router_builder.add_conditional_edges(
    "categorize_request",
    route_decision,
    {
        "standard_answer": "standard_answer",
        "browser_helper": "browser_helper",
        "developer_helper": "developer_helper"
    }
)

router_builder.add_edge(START, "categorize_request")
router_builder.add_edge("standard_answer", END)

graph = router_builder.compile()
