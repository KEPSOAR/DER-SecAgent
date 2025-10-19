from langgraph.graph import StateGraph, START, END
from .states import soar_input, report_state, caution_eval_state
from kepsoar.llm.agents import script_gen_agent, caution_eval_agent, report_gen_agent
from kepsoar.graph.states import operation_mode

def build():
    script_builder = StateGraph(soar_input, input=soar_input, output=caution_eval_state)
    script_builder.add_node("script_gen", script_gen_agent)
    script_builder.add_node("eval_caution_level", caution_eval_agent)
    script_builder.add_edge(START, "script_gen")
    script_builder.add_edge("script_gen", "eval_caution_level")
    script_sub = script_builder.compile()
    report_builder = StateGraph(report_state, input=soar_input, output=report_state)
    report_builder.add_node("eval_caution_level", caution_eval_agent)
    report_builder.add_node("report_gen", report_gen_agent)
    report_builder.add_conditional_edges(
        START,
        lambda s: "eval" if s.get("is_script_changed", False) else "direct",
        path_map={
            "eval":   "eval_caution_level",
            "direct": "report_gen",
        }
    )
    report_builder.add_edge("eval_caution_level", "report_gen")
    report_builder.add_edge("report_gen", END)
    report_sub = report_builder.compile()

    graph = StateGraph(input=soar_input, output=report_state)
    graph.add_node("script_path", script_sub)
    graph.add_node("report_path", report_sub)

    graph.add_conditional_edges(
        START,
        lambda s: s["mode"],
        path_map={
            operation_mode.SCRIPT_GEN: "script_path",
            operation_mode.REPORT_GEN: "report_path"
        }
    )
    graph.add_edge("script_path", END)
    graph.add_edge("report_path", END)

    return graph.compile()
