# kepsoar/utils/prompts.py
from __future__ import annotations
from typing import Callable, Dict, Optional

from kepsoar.graph.states import soar_input, script_engineering_type


def _log_entry(state: soar_input) -> str:
    return (
        f'Log entry:\n'
        f'Time: {state["event_time"]}\n'
        f'Device IP: {state["device_ip"]}\n'
        f'Device Name: {state["device_name"]}\n'
        f'Source Institution Code: {state["source_institution_code"]}\n'
        f'Source IP: {state["source_ip"]}\n'
        f'Source Port: {state["source_port"]}\n'
        f'Source Asset Name: {state["source_asset_name"]}\n'
        f'Source Country: {state["source_country"]}\n'
        f'Destination Institution Code: {state["dest_institution_code"]}\n'
        f'Destination IP: {state["dest_ip"]}\n'
        f'Destination Port: {state["dest_port"]}\n'
        f'Destination Asset Name: {state["dest_asset_name"]}\n'
        f'Destination Country: {state["dest_country"]}\n'
        f'Attack Type: {state["attack_type"].name}\n'
    )


def build_zero_shot(state: soar_input, history: str = "") -> str:
    return f"""You are a security engineer specialized in iptables.
You are provided with a TCP log entry.
Based on these, generate a minimal set of valid, actual CLI commands.
Do not output multiple alternative solutions or any text other than the commands.
Output each command on a separate commands exactly as you would type them in a terminal.

{_log_entry(state)}""".rstrip()


def build_few_shot(state: soar_input, history: str = "") -> str:
    return f"""You are a security engineer specialized in iptables.
You are provided with a TCP log entry and a concise history of previously effective iptables commands.
Based on these, generate a minimal set of valid, actual CLI commands.
If a similar command exists in the history, reuse and adjust it.
Do not output multiple alternative solutions or any text other than the commands.
Output each command on a separate commands exactly as you would type them in a terminal.

{_log_entry(state)}
Previous Response History:
{history}""".rstrip()


def build_cot(state: soar_input, history: str = "") -> str:
    # 주의: 내부 체크리스트의 {dest_ip}/{device_ip}/{source_ip} 등은 변수명 그대로 보여야 하므로 {{ }}로 이스케이프
    return f"""You are a senior security engineer specialized in iptables.

You are given a single TCP log entry and a concise history of previously effective iptables commands. 
Your task is to produce the minimal set of valid, actual CLI commands. 
If a similar command exists in the history, reuse it and adjust arguments.

Think step by step **internally only**. Use a hidden scratchpad to reason about direction, chain, action, and flags. 
**Never** reveal your reasoning or the scratchpad. **Only output the final commands.**

INTERNAL REASONING CHECKLIST (DO NOT OUTPUT):
1) Parse fields from the log:
   - event_time, device_ip, device_name
   - source_institution_code, source_ip, source_port, source_asset_name, source_country
   - dest_institution_code, dest_ip, dest_port, dest_asset_name, dest_country
   - attack_type (string name)

2) Decide packet direction and chain:
   - if {{dest_ip}} == {{device_ip}} → chain=INPUT
   - else if {{source_ip}} == {{device_ip}} → chain=OUTPUT
   - else → chain=FORWARD

3) Choose action:
   - Default to DROP for malicious/suspicious attack_type.
   - If history clearly shows ACCEPT for the same service/tuple pattern under similar context, follow history and ACCEPT.
   - Prefer minimal rules (usually 1). Only add symmetric/return-path rules if history consistently does so.

4) Reuse & adjust:
   - Search "Previous Response History" for the closest matching rule (same chain/service/port/protocol/interface style).
   - Reuse flag order and modules (-m conntrack/state, -i/-o, --syn, etc.) and only swap IPs/ports as needed.

5) Compose a valid iptables command:
   - Table: filter (implicit), Protocol: -p tcp
   - Addresses/ports: -s {{source_ip}}, -d {{dest_ip}}, --sport {{source_port}} (only if needed), --dport {{dest_port}}
   - Jump: -j DROP or -j ACCEPT
   - Keep formatting and option order consistent with reused history when applicable.

6) Validation:
   - No placeholders; substitute all {{…}} with actual values from inputs/history analysis.
   - No comments, no explanations, no headings, no code fences.
   - One command per line. No alternative solutions.

INPUTS:

{_log_entry(state)}
Previous Response History (FOR INTERNAL REASONING ONLY; DO NOT ECHO):
{history}

OUTPUT REQUIREMENTS (FINAL):
- Output only the final iptables command(s), exactly as you would type them in a terminal.
- One command per line.
- No extra text, no explanations, no alternatives.""".rstrip()


def build_tot(state: soar_input, history: str = "") -> str:
    return f"""You are a senior security engineer specialized in iptables.

Task:
Given a single TCP log entry and a concise history of previously effective iptables commands, produce the minimal set of valid CLI commands. If a similar command exists in history, reuse and adjust it.

THINK IN A TREE (INTERNAL ONLY):
- Build 4 branches of candidate solutions (width ≤4, depth ≤2).
- Each branch proposes 1–3 iptables commands and a brief internal rationale.
- After expanding/refining, score each branch with the rubric below.
- Select the top-scoring branch. DO NOT output your reasoning or scores.

BRANCHING STRATEGIES (SUGGESTED, INTERNAL ONLY):
A) Reuse the closest history rule; adjust only IP/port.
B) Minimal fresh rule: -p tcp, -s, -d, --dport, -j DROP/ACCEPT.
C) Stateful variant if history uses it: -m conntrack --ctstate NEW.
D) Interface-anchored variant if history pins interfaces: -i/-o.
(Only add symmetric/return-path rules if history consistently includes them.)

SCORING RUBRIC (INTERNAL ONLY, 0–10):
- Correct chain selection (INPUT/OUTPUT/FORWARD) [0–3]
- Policy minimality (fewest rules/flags while safe) [0–3]
- Consistency with history style/order [0–2]
- Syntax validity & safety (no placeholders, sane flags) [0–2]
Tie-breakers: higher safety → fewer rules → closer to history style.

INTERNAL CHECKLIST (DO NOT OUTPUT):
1) Parse fields: event_time, device_ip, device_name,
   source_institution_code, source_ip, source_port, source_asset_name, source_country,
   dest_institution_code, dest_ip, dest_port, dest_asset_name, dest_country,
   attack_type (string name).
2) Decide chain:
   - if {{dest_ip}} == {{device_ip}} → INPUT
   - else if {{source_ip}} == {{device_ip}} → OUTPUT
   - else → FORWARD
3) Choose action:
   - Default DROP for malicious/suspicious attack_type.
   - If history clearly ACCEPTs the same service/context, follow history.
4) Compose commands:
   - table filter (implicit), -p tcp
   - -s {{source_ip}} (optional per history), -d {{dest_ip}}, --dport {{dest_port}}
   - optional: -m conntrack --ctstate NEW, -i/-o per history
   - -j DROP or -j ACCEPT
   - Avoid --sport unless history uses it.
5) Validate:
   - Replace all placeholders; no comments; no alternatives.
   - One command per line.

INPUTS:

{_log_entry(state)}
Previous Response History (FOR INTERNAL REASONING ONLY; DO NOT ECHO):
{history}

OUTPUT REQUIREMENTS (FINAL):
- Output only the final iptables command(s), exactly as you would type them in a terminal.
- One command per line.
- No extra text, no explanations, no alternatives.""".rstrip()


BUILDERS: Dict[script_engineering_type, Callable[[soar_input, str], str]] = {
    script_engineering_type.ZERO_SHOT: build_zero_shot,
    script_engineering_type.FEW_SHOT:  build_few_shot,
    script_engineering_type.COT:       build_cot,
    script_engineering_type.TOT:       build_tot,
}

def build_prompt(kind: script_engineering_type, state: soar_input, history: Optional[str] = "") -> str:
    return BUILDERS[kind](state, history or "")