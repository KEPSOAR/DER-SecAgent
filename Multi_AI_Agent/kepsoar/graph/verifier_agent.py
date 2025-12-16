# kepsoar/llm/agents/verifier_agent.py (예시)
def verifier_agent(state: dict) -> dict:
    # ---- script 검증 ----
    if "script" in state and "report" not in state:
        attempts = int(state.get("script_verify_attempts", 0)) + 1

        script = state.get("script", "")
        # TODO: LLM 기반 검증/수정 로직
        # - 안전 정책 위반 여부(위험 명령, 과도한 destructive, 오탐 유발 등)
        # - 문법/실행 가능성(쉘/파이썬/파워쉘 등)
        # - 환경 적합성(경로/권한/의존성)
        verified = True
        feedback = ""

        # 예: 문제가 있으면 verified=False + 피드백 제공
        # verified = False
        # feedback = "iptables rule이 너무 broad합니다. 특정 IP/port로 제한하세요."

        # 예: verifier가 script를 직접 “수정”하는 전략도 가능(성능↑)
        # fixed_script = script  # 또는 수정본
        fixed_script = script

        return {
            "script_verify_attempts": attempts,
            "script_verified": verified,
            "script_verifier_feedback": feedback,
            "script": fixed_script,
            "is_script_changed": state.get("is_script_changed", False) or (fixed_script != script),
        }

    # ---- report 검증 ----
    if "report" in state:
        attempts = int(state.get("report_verify_attempts", 0)) + 1

        report = state.get("report", "")
        # TODO: LLM 기반 검증/수정 로직
        # - 누락 필드/환각(사실과 다른 주장)
        # - 이벤트 정보와의 정합성
        # - 보안 관제 보고서 포맷 준수
        verified = True
        feedback = ""
        fixed_report = report

        return {
            "report_verify_attempts": attempts,
            "report_verified": verified,
            "report_verifier_feedback": feedback,
            "report": fixed_report,
        }

    # fallback
    return {}
