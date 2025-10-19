import requests
import os
from dotenv import load_dotenv
from st2common.runners.base_action import Action # type: ignore

# Load environment variables from .env
load_dotenv('/opt/stackstorm/packs/kepsoar/.env')

class AlertHistory(Action):
    def run(self, script, log_id, caution):
        datas = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"AI Agent로 부터 만들어진 대응 스크립트: ```\n{script}\n```"
                }
            },
            {
                "type": "divider",
            },
            {
                "type": "context",
                "elements": [
                    {
                    "type": "mrkdwn",
                    "text": "👀 어떤 공격에 대한 대응인지 알고 싶다면 detection-log를 참고해주세요",
                    },
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*실행될 스크립트입니다*",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```\n{script}\n```",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "대처 스크립트 실행",
                    },
                    "style": "primary",
                    "value": f"{script}",
                    "action_id": "execute_script",
                    },
                    {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "대처 스크립트 수정",
                    },
                    "style": "danger",
                    "value": f"{script}",
                    "action_id": "edit_script",
                    },
                ],
                },
            ],
            "metadata": {
                "event_type": "agent_value",
                "event_payload": {
                    "log_id": log_id,
                    "caution_level": caution,
                }
            }
        }
        headers = {"Content-type": "application/json"}
        url = os.getenv("SLACK_HISTORY_URL")
        print(datas)
        try:
            response = requests.post(url, headers=headers, json=datas)
            return (True, response)
        except:
            return (False, "Post failed")
