# This is text gen. version may change to chat version
import requests
from langchain_ollama import OllamaLLM
from kepsoar.graph.states import soar_input, caution_eval_state, report_state, operation_mode, script_engineering_type
from kepsoar.utils.chain_of_thought import gen_COT_prompt
from kepsoar.db.db_connect import fetch_history_storage
import os
from dotenv import load_dotenv
import urllib3
from kepsoar.utils.prompts import build_prompt
urllib3.disable_warnings()

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3")
REPORT_WEBHOOK_URL = os.getenv("REPORT_WEBHOOK_URL")
SCRIPT_WEBHOOK_URL = os.getenv("SCRIPT_WEBHOOK_URL")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN")


def mk_cot_prompt(state: soar_input) -> str:
    history_logs = fetch_history_storage(history_type=state["attack_type"].value)
    return gen_COT_prompt(history_logs)

script_gen_llm = OllamaLLM(model=OLLAMA_MODEL_NAME, base_url=OLLAMA_BASE_URL)

def script_gen_agent(state: soar_input) -> soar_input:
    raw_kind = state.get("script_engineering", script_engineering_type.ZERO_SHOT)
    if isinstance(raw_kind, script_engineering_type):
        kind = raw_kind
    else:
        kind = script_engineering_type(str(raw_kind).lower())

    history = ""
    if kind in {script_engineering_type.FEW_SHOT, script_engineering_type.COT, script_engineering_type.TOT}:
        try:
            history = mk_cot_prompt(state) or ""
        except Exception:
            history = ""

    prompt = build_prompt(kind, state, history)
    script_output = script_gen_llm.invoke(prompt)
    state["script"] = script_output

    return state

caution_level_eval_llm = OllamaLLM(model=OLLAMA_MODEL_NAME, base_url=OLLAMA_BASE_URL)

def caution_eval_agent(state: soar_input) -> caution_eval_state:
    prompt = f"""You are a system safety engineer. Evaluate the following CLI script that is intended to be executed on a server.
Determine if executing this script will cause permanent or irreversible changes to the server.
Output only "true" if it will cause such changes or "false" if it will not.
Script:
{state["script"]}
"""
    eval_output = caution_level_eval_llm.invoke(prompt)
    eval_result = eval_output.strip().lower()
    need_caution = True if eval_result == "true" else False

    if state["mode"] == operation_mode.SCRIPT_GEN:
        url = SCRIPT_WEBHOOK_URL
        payload = {
            "log_id": state["id"],
            "script": state["script"],
            "caution": need_caution
        }
        headers = {
            "St2-Api-Key": WEBHOOK_TOKEN,
        }

        response = requests.post(url, json=payload, verify=False, headers=headers)
        print("Status Code:", response.status_code)
        print("Response Body:", response.text)

    return {
        "id": state["id"],
        "event_time": state["event_time"],
        "device_ip": state["device_ip"],
        "device_name": state["device_name"],
        "source_institution_code": state["source_institution_code"],
        "source_ip": state["source_ip"],
        "source_mac": state["source_mac"],
        "source_port": state["source_port"],
        "source_asset_name": state["source_asset_name"],
        "source_country": state["source_country"],
        "dest_institution_code": state["dest_institution_code"],
        "dest_ip": state["dest_ip"],
        "dest_mac": state["dest_mac"],
        "dest_port": state["dest_port"],
        "dest_asset_name": state["dest_asset_name"],
        "dest_country": state["dest_country"],
        "protocol": state["protocol"],
        "attack_type": state["attack_type"],
        "account": state["account"],
        "script": state["script"],
        "caution": need_caution
    }

report_gen_llm = OllamaLLM(model=OLLAMA_MODEL_NAME, base_url=OLLAMA_BASE_URL)

def report_gen_agent(state: caution_eval_state) -> report_state:
    prompt = f"""[System Instruction]
You are a cyber security expert and a professional report writer.
Based on attack time, type, and asset information, write a clear and structured security incident report.

[User Instruction]
Below is data extracted via rules for a security incident in a DER (Distributed Energy Resources) environment. Using this information, write a "DER Security Incident Report" in English that includes: attack overview, attacker information, asset information, response actions and timeline, impact/severity, and additional recommendations.

### Extracted Data (example)
- Attack_Type: {state["attack_type"]}
- Attack_Time:
- Response_Time:
- Severity_Level:
- DER_IP:
- DER_Address:
- Attacker_IP:
- Attacker_Address:

### Output Requirements
1. Report title: "DER Security Incident Report"
2. Attack overview: time, attack type, presumed motivation
3. Attacker information: Attacker_IP, Attacker_Address
4. Asset information (DER): DER_IP, DER_Address
5. Response actions and time: detection and response completion timestamps
6. Impact/Severity: risk level and scope based on Severity_Level
7. Additional recommendations: 1–2 hardening actions

### Format
- Within one A4 page, English
- Natural and concise sentences
- Use subheadings or bullet points if helpful

[End of Instruction]
"""

    report = report_gen_llm.invoke(prompt)
    url = REPORT_WEBHOOK_URL
    payload = {
    "log_id": state["id"],
    "script": state["script"],
    "report": report,
    "caution": True
    }
    headers = {
            "St2-Api-Key": WEBHOOK_TOKEN,
    }

    response = requests.post(url, json=payload, verify=False, headers=headers)
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

    return {"id": state["id"],
        "event_time": state["event_time"],
        "device_ip": state["device_ip"],
        "device_name": state["device_name"],
        "source_institution_code": state["source_institution_code"],
        "source_ip": state["source_ip"],
        "source_mac": state["source_mac"],
        "source_port": state["source_port"],
        "source_asset_name": state["source_asset_name"],
        "source_country": state["source_country"],
        "dest_institution_code": state["dest_institution_code"],
        "dest_ip": state["dest_ip"],
        "dest_mac": state["dest_mac"],
        "dest_port": state["dest_port"],
        "dest_asset_name": state["dest_asset_name"],
        "dest_country": state["dest_country"],
        "protocol": state["protocol"],
        "attack_type": state["attack_type"],
        "account": state["account"],
        "script": state["script"],
        "caution": True,
        "report": report
        }
