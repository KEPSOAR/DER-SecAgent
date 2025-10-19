import sys
import requests
import os
from dotenv import load_dotenv
from st2common.runners.base_action import Action # type: ignore

# Load environment variables from .env
load_dotenv('/opt/stackstorm/packs/kepsoar/.env')


class AlertDetectionIDS(Action):
    def run(self, event_time, device_ip, device_name, source_institution_code, source_ip, source_port, source_asset_name, source_country, source_mac, dest_institution_code, dest_ip, dest_port, dest_asset_name, dest_country, dest_mac, protocol, action, attack_type, account, risk_level):
        datas = {
            "text": (
                f"IDS Alert Detected\n"
                f"Event Time: {event_time}\n"
                f"Device IP: {device_ip}\n"
                f"Device Name: {device_name}\n"
                f"Source Institution Code: {source_institution_code}\n"
                f"Source IP: {source_ip} (Port: {source_port})\n"
                f"Source Asset Name: {source_asset_name}\n"
                f"Source Country: {source_country}\n"
                f"Source MAC: {source_mac}\n"
                f"Destination Institution Code: {dest_institution_code}\n"
                f"Destination IP: {dest_ip} (Port: {dest_port})\n"
                f"Destination Asset Name: {dest_asset_name}\n"
                f"Destination Country: {dest_country}\n"
                f"Destination MAC: {dest_mac}"
                f"Protocol: {protocol}\n"
                f"Action: {action}\n"
                f"Attack Type: {attack_type}\n"
                f"Account: {account}\n"
                f"Risk Level: {risk_level}\n"
            )
        }
        headers = {"Content-type": "application/json"}
        url = os.getenv("SLACK_DETECTION_URL")

        try:
            response = requests.post(url, headers=headers, json=datas)
            return (True, response)
        except:
            return (False, "Post failed")
