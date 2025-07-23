import logging
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, AIMessage
from langchain_openai import ChatOpenAI

from run_program.utils.prompt import SYSTEM_PROMPT
from run_program.utils.tools import find_shortcut, run_program
from run_program.utils.state import Program, ProgramRunner


load_dotenv()
SHORTCUT_NAMES = list(find_shortcut())
LLM = ChatOpenAI(model="gpt-4o-mini")

def find_program_name(state: ProgramRunner) -> ProgramRunner:
    """Analyze request from user."""

    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(programs=SHORTCUT_NAMES))
    human_msg = state["messages"][-1]
    decision = LLM.with_structured_output(Program).invoke([sys_msg, human_msg])
    logging.info(f"Decision: '{decision.program_name}'")
    return {"program_name": decision.program_name}

def route_decision(state: ProgramRunner) -> str:
    """Route next step """
    if state["program_name"] in SHORTCUT_NAMES:
        return "name_exist"
    else:
        return "name_not_exist"
    
def open_program(state: ProgramRunner) ->ProgramRunner:
    """Run program local on PC"""
    
    try:
        run_program(name=state["program_name"])
    except Exception as e:
        logging.info(f"Error: {e}")
        ai_msg = AIMessage(content=f"Program {state["program_name"].rstrip(".lnk")} can't started")
    ai_msg = AIMessage(content=f"Program {state["program_name"].rstrip(".lnk")} started")
    return {"messages": [ai_msg]}
