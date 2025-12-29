# build_graph.py
from langgraph.graph import StateGraph, START, END
from .states import soar_input, report_state, caution_eval_state
from kepsoar.llm.agents import (
    script_gen_agent,
    caution_eval_agent,
    report_gen_agent,
    verifier_agent,  # ✅ Added (use a single verifier for both script and report)
)
from kepsoar.graph.states import operation_mode

MAX_VERIFY_RETRIES = 2  # ✅ Number of retries (1–3 recommended)

def build():
    # ---------------------------
    # 1) Script Subgraph
    # ---------------------------
    script_builder = StateGraph(soar_input, input=soar_input, output=caution_eval_state)

    script_builder.add_node("script_gen", script_gen_agent)
    script_builder.add_node("verify_script", verifier_agent)         # ✅ Added
    script_builder.add_node("eval_caution_level", caution_eval_agent)

    script_builder.add_edge(START, "script_gen")
    script_builder.add_edge("script_gen", "verify_script")

    # ✅ Branch based on verification result (on fail, loop back to regenerate)
    def script_verify_router(s: dict) -> str:
        verified = s.get("script_verified", True)
        attempts = s.get("script_verify_attempts", 0)
        if verified:
            return "ok"
        if attempts < MAX_VERIFY_RETRIES:
            return "retry"
        return "giveup"

    script_builder.add_conditional_edges(
        "verify_script",
        script_verify_router,
        path_map={
            "ok": "eval_caution_level",
            "retry": "script_gen",
            "giveup": "eval_caution_level",  # ✅ If no retries left, pass to caution evaluation (may set high caution)
        },
    )

    script_builder.add_edge("eval_caution_level", END)
    script_sub = script_builder.compile()

    # ---------------------------
    # 2) Report Subgraph
    # ---------------------------
    report_builder = StateGraph(report_state, input=soar_input, output=report_state)

    report_builder.add_node("eval_caution_level", caution_eval_agent)
    report_builder.add_node("report_gen", report_gen_agent)
    report_builder.add_node("verify_report", verifier_agent)         # ✅ Added (same verifier)

    # From START, decide whether to go through caution eval based on is_script_changed
    report_builder.add_conditional_edges(
        START,
        lambda s: "eval" if s.get("is_script_changed", False) else "direct",
        path_map={
            "eval": "eval_caution_level",
            "direct": "report_gen",
        },
    )

    report_builder.add_edge("eval_caution_level", "report_gen")
    report_builder.add_edge("report_gen", "verify_report")

    # ✅ Branch based on report verification (on fail, loop back to regenerate report)
    def report_verify_router(s: dict) -> str:
        verified = s.get("report_verified", True)
        attempts = s.get("report_verify_attempts", 0)
        if verified:
            return "ok"
        if attempts < MAX_VERIFY_RETRIES:
            return "retry"
        return "giveup"

    report_builder.add_conditional_edges(
        "verify_report",
        report_verify_router,
        path_map={
            "ok": END,
            "retry": "report_gen",
            "giveup": END,  # ✅ If no retries left, finish (feedback remains in state)
        },
    )

    report_sub = report_builder.compile()

    # ---------------------------
    # 3) Parent Graph (mode)
    # ---------------------------
    graph = StateGraph(input=soar_input, output=report_state)
    graph.add_node("script_path", script_sub)
    graph.add_node("report_path", report_sub)

    graph.add_conditional_edges(
        START,
        lambda s: s["mode"],
        path_map={
            operation_mode.SCRIPT_GEN: "script_path",
            operation_mode.REPORT_GEN: "report_path",
        },
    )

    graph.add_edge("script_path", END)
    graph.add_edge("report_path", END)

    return graph.compile()
