# build_graph.py
from langgraph.graph import StateGraph, START, END
from .states import soar_input, report_state, caution_eval_state
from kepsoar.llm.agents import (
    script_gen_agent,
    caution_eval_agent,
    report_gen_agent,
    verifier_agent,  # ✅ 추가 (단일 verifier를 script/report 모두에 사용)
)
from kepsoar.graph.states import operation_mode

MAX_VERIFY_RETRIES = 2  # ✅ 재시도 횟수(원하면 1~3 정도 권장)

def build():
    # ---------------------------
    # 1) Script Subgraph
    # ---------------------------
    script_builder = StateGraph(soar_input, input=soar_input, output=caution_eval_state)

    script_builder.add_node("script_gen", script_gen_agent)
    script_builder.add_node("verify_script", verifier_agent)         # ✅ 추가
    script_builder.add_node("eval_caution_level", caution_eval_agent)

    script_builder.add_edge(START, "script_gen")
    script_builder.add_edge("script_gen", "verify_script")

    # ✅ 검증 결과에 따라 분기 (fail이면 재생성 루프)
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
            "giveup": "eval_caution_level",  # ✅ 더 이상 재시도 못하면 경고평가로 넘겨서 높은 caution으로 처리 가능
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
    report_builder.add_node("verify_report", verifier_agent)         # ✅ 추가 (같은 verifier)

    # START에서 is_script_changed 여부에 따라 caution eval을 거칠지 결정
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

    # ✅ report 검증 결과에 따라 분기 (fail이면 report 재생성 루프)
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
            "giveup": END,  # ✅ 더 이상 재시도 못하면 일단 종료(피드백은 state에 남김)
        },
    )

    report_sub = report_builder.compile()

    # ---------------------------
    # 3) Parent Graph (mode 분기)
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
