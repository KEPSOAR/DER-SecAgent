# TODO
def gen_COT_prompt(logs: list[dict]) -> str:
    if not logs:
        return ''

    prompt = 'Response history for same attack type:\n'
    for i, log in enumerate(logs, 1):
        prompt += f'\nRelated Log {i}:\n'
        prompt += f'ID: {log["id"]}\n'
        prompt += f'Event Time: {log["event_time"]}\n'
        prompt += f'Device IP: {log["device_ip"]}\n'
        prompt += f'Device Name: {log["device_name"]}\n'
        prompt += f'Source Institution Code: {log["source_institution_code"]}\n'
        prompt += f'Source IP: {log["source_ip"]}\n'
        prompt += f'Source Port: {log["source_port"]}\n'
        prompt += f'Source Asset Name: {log["source_asset_name"]}\n'
        prompt += f'Source Country: {log["source_country"]}\n'
        prompt += f'Source MAC: {log["source_mac"]}\n'
        prompt += f'Destination Institution Code: {log["dest_institution_code"]}\n'
        prompt += f'Destination IP: {log["dest_ip"]}\n'
        prompt += f'Destination Port: {log["dest_port"]}\n'
        prompt += f'Destination Asset Name: {log["dest_asset_name"]}\n'
        prompt += f'Destination Country: {log["dest_country"]}\n'
        prompt += f'Destination MAC: {log["dest_mac"]}\n'
        prompt += f'Protocol: {log["protocol"]}\n'
        prompt += f'Attack Type: {log["attack_type"]}\n'
        prompt += f'Account: {log["account"]}\n'
        prompt += f'Risk Level: {log["risk_level"]}\n'
        prompt += f'Given Script: {log["given_script"]}\n'
        prompt += f'Executed Script: {log["executed_script"]}\n'
        prompt += f'Changed Reason: {log["changed_reason"]}\n'
        prompt += f'Caution: {log["caution_level"]}\n'
    return prompt
