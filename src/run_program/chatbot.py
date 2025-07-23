from langgraph.graph import StateGraph, END

from run_program.utils.nodes import find_program_name, open_program, route_decision
from run_program.utils.state import ProgramRunner


builder = StateGraph(ProgramRunner)
builder.add_node(find_program_name)
builder.add_node(open_program)
builder.set_entry_point("find_program_name")
builder.add_conditional_edges(
    "find_program_name",
    route_decision,
    {
        "name_exist": "open_program",
        "name_not_exist": END
    }
)
builder.add_edge("find_program_name", "open_program")
builder.set_finish_point("open_program")
