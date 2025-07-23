import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from personal_helper.utils.prompt import ROUTE_REQUEST_PROMPT
from personal_helper.utils.state import Helper, RouteRequest

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

def categorize_request(state: Helper) -> Helper:
    """Categorize what kind of url user want to see."""

    sys_msg = SystemMessage(content=ROUTE_REQUEST_PROMPT)
    decision = llm.with_structured_output(RouteRequest).invoke([sys_msg] + state["messages"])
    logging.info(f"Decision in helper: {decision}")
    return {"step": decision.step}

def route_decision(state: Helper) -> str:
    """Route next step """

    if state["step"] == "answer":
        return "standard_answer"
    elif state["step"] == "browser":
        return "browser_helper"
    elif state["step"] == "programming":
        return "developer_helper"
    elif state["step"] == "run_program":
        return "run_program"
    
def standard_answer(state: Helper) ->Helper:
    """Answer for users request"""

    llm = ChatOpenAI(model="o4-mini")
    result = llm.invoke(state["messages"])
    return {"messages": result}