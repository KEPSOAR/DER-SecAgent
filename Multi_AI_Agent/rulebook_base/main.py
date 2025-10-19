import sys
from typing import List
import os
import requests

from kepsoar.db.db_connect import fetch_log_storage
from kepsoar.utils.parser import parse
from kepsoar.graph.states import attack_type

RULE_BOOK: dict[attack_type, List[str]] = {
    attack_type.DoS: [
        "iptables -A INPUT -s {src} -p {proto} --dport {dport} -m limit --limit 25/minute --limit-burst 100 -j ACCEPT",
        "iptables -A INPUT -s {src} -j DROP",
    ],
    attack_type.Probe: [
        "iptables -A INPUT -s {src} -j DROP",
    ],
    attack_type.R2L: [
        "iptables -A INPUT -s {src} -j LOG --log-prefix \"R2L: \"",
        "iptables -A INPUT -s {src} -j DROP",
    ],
    attack_type.U2R: [
        "iptables -A INPUT -s {src} -j LOG --log-prefix \"U2R: \"",
        "iptables -A INPUT -s {src} -j DROP",
    ],
    attack_type.MITM: [
        "iptables -A INPUT -s {src} -j DROP",
        "iptables -A OUTPUT -d {src} -j DROP",
    ],
    attack_type.BruteForce: [
        "iptables -A INPUT -s {src} -p tcp --dport 22 -m recent --set --name SSH",
        "iptables -A INPUT -s {src} -p tcp --dport 22 -m recent --update --seconds 60 --hitcount 5 --name SSH -j DROP",
    ],
}

def build_rulebook_script(state: dict) -> str:
    atk = state["attack_type"]
    tmpl = RULE_BOOK.get(atk) or [
        "iptables -A INPUT -s {src} -p {proto} --dport {dport} -j DROP"
    ]

    src   = state.get("source_ip")
    proto = (state.get("protocol") or "tcp").lower()
    dport = state.get("dest_port") or 0
    try:
        dport = int(dport)
    except Exception:
        dport = 0

    filled = [cmd.format(src=src, proto=proto, dport=dport) for cmd in tmpl]
    return "\n".join(filled).strip() + "\n"

def send_script_webhook(state: dict, need_caution: bool = False) -> None:
    url = os.getenv("SCRIPT_WEBHOOK_URL")
    token = os.getenv("WEBHOOK_TOKEN")

    if not url:
        print("[rulebook] WARN: SCRIPT_WEBHOOK_URL is not set. Skip sending.")
        return

    payload = {
        "log_id": state["id"],
        "script": state["script"],
        "caution": need_caution,
    }
    headers = {"St2-Api-Key": token} if token else {}

    try:
        resp = requests.post(url, json=payload, verify=False, headers=headers, timeout=10)
        print("Status Code:", resp.status_code)
        print("Response Body:", resp.text)
    except Exception as e:
        print("[rulebook] webhook exception:", e)

def main(key: int) -> None:
    rows = fetch_log_storage(key)
    if not rows:
        print(f"[rulebook] no log rows for key={key}")
        return

    state = parse(rows)

    script = build_rulebook_script(state)
    state["script"] = script

    print("== RULEBOOK SCRIPT ==")
    print(script, end="")
    print("=" * 80)

    send_script_webhook(state, need_caution=False)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 -m rulebook_base.main <key>")
        sys.exit(1)
    try:
        key_param = int(sys.argv[1])
    except ValueError:
        print("key must be an integer")
        sys.exit(1)
    main(key_param)