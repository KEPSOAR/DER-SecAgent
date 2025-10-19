from kepsoar.graph.states import soar_input, attack_type
from datetime import datetime

def parse(log: list[dict]) -> soar_input:
    input: soar_input
    for row in log:
        event_time_val = row['event_time'] if isinstance(row['event_time'], datetime) else datetime.strptime(row['event_time'], "%Y-%m-%d %H:%M:%S")

        attack_type_val = attack_type(row['attack_type'])

        input_item: soar_input = {
            "id": row['id'],
            "event_time": event_time_val,
            "device_ip": row['device_ip'],
            "device_name": row['device_name'],
            "source_institution_code": row['source_institution_code'],
            "source_ip": row['source_ip'],
            "source_port": row['source_port'],
            "source_asset_name": row['source_asset_name'],
            "source_country": row['source_country'],
            "source_mac": row['source_mac'],
            "dest_institution_code": row['dest_institution_code'],
            "dest_ip": row['dest_ip'],
            "dest_port": row['dest_port'],
            "dest_asset_name": row['dest_asset_name'],
            "dest_country": row['dest_country'],
            "dest_mac": row['dest_mac'],
            "protocol": row['protocol'],
            "attack_type": attack_type_val,
            "account": row['account'],
            "script": "",
            "chain_of_thought": ""
        }
        input = input_item
    return input

def parse_from_history(log: list[dict]) -> soar_input:
    input: soar_input
    for row in log:
        event_time_val = row['event_time'] if isinstance(row['event_time'], datetime) else datetime.strptime(row['event_time'], "%Y-%m-%d %H:%M:%S")

        attack_type_val = attack_type(row['attack_type'])

        input_item: soar_input = {
            "id": row['id'],
            "event_time": event_time_val,
            "device_ip": row['device_ip'],
            "device_name": row['device_name'],
            "source_institution_code": row['source_institution_code'],
            "source_ip": row['source_ip'],
            "source_port": row['source_port'],
            "source_asset_name": row['source_asset_name'],
            "source_country": row['source_country'],
            "source_mac": row['source_mac'],
            "dest_institution_code": row['dest_institution_code'],
            "dest_ip": row['dest_ip'],
            "dest_port": row['dest_port'],
            "dest_asset_name": row['dest_asset_name'],
            "dest_country": row['dest_country'],
            "dest_mac": row['dest_mac'],
            "protocol": row['protocol'],
            "attack_type": attack_type_val,
            "account": row['account'],
            "script": row.get('executed_script', ''),
            "chain_of_thought": "",
            "caution_level": row['caution_level']
        }
        input = input_item
    return input
