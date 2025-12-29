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
                        "text": f"*The response for the script has been completed and a report has been generated!*\nScript\n{script}\nReport\n{report}"
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
                        "text": "👀 To see which attack this response pertains to, please check the history log.",
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
