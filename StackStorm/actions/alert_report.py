import requests
import os
from dotenv import load_dotenv
from st2common.runners.base_action import Action # type: ignore

# Load environment variables from .env
load_dotenv('/opt/stackstorm/packs/kepsoar/.env')

class AlertReport(Action):
    def run(self, report, script):
        datas = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*해당 script에 대한 대처가 완료되었고 보고서가 생성되었습니다!*\n스크립트\n{script}\n보고서\n{report}"
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
                        "text": "👀 어떤 공격에 대한 대처인지 알고 싶다면 history-log를 참고해주세요",
                        },
                    ],
                },
            ],
        }
        headers = {"Content-type": "application/json"}
        url = os.getenv("SLACK_REPORT_URL")
        print(datas)
        try:
            response = requests.post(url, headers=headers, json=datas)
            return (True, response)
        except:
            return (False, "Post failed")
