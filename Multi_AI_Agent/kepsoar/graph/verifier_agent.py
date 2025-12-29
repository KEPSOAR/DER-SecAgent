# kepsoar/llm/agents/verifier_agent.py (example)
def verifier_agent(state: dict) -> dict:
    # ---- script verification ----
    if "script" in state and "report" not in state:
        attempts = int(state.get("script_verify_attempts", 0)) + 1

        script = state.get("script", "")
        # TODO: LLM-based verification/fix logic
        # - Security policy violations (dangerous commands, overly destructive, false positives, etc.)
        # - Syntax/executability (shell/python/powershell, etc.)
        # - Environment suitability (paths/permissions/dependencies)
        verified = True
        feedback = ""

        # Example: if there is a problem, set verified=False and provide feedback
        # verified = False
        # feedback = "The iptables rule is too broad. Restrict it to a specific IP/port."

        # Example: allow the verifier to directly "fix" the script (better performance)
        # fixed_script = script  # or a modified version
        fixed_script = script

        return {
            "script_verify_attempts": attempts,
            "script_verified": verified,
            "script_verifier_feedback": feedback,
            "script": fixed_script,
            "is_script_changed": state.get("is_script_changed", False) or (fixed_script != script),
        }

    # ---- report verification ----
    if "report" in state:
        attempts = int(state.get("report_verify_attempts", 0)) + 1

        report = state.get("report", "")
        # TODO: LLM-based verification/fix logic
        # - Missing fields/hallucinations (claims not grounded in facts)
        # - Consistency with event information
        # - Compliance with SOC report format
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
