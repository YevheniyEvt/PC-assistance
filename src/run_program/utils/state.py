from langgraph.graph import MessagesState
from pydantic import BaseModel, Field

from run_program.utils.tools import SHORTCUT_NAMES


class ProgramRunner(MessagesState):
    program_name: str

class Program(BaseModel):
    program_name: str = Field(
        description="Name of program that user want to run",
        examples=SHORTCUT_NAMES
    )