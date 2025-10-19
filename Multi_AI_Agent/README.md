# kepsoar

python script for langgraph

## dependency:
아래를 pip install 해주세요

- langchain
- langchain-community
- langchain-ollama
- langgraph
- mysql-connector-python (not supported yet)

- google
- cloud-sql-python-connector
- sqlalchemy
- pymysql

아래는 시스템에 설치되어 있어야 합니다

- ollama, models store in local (to change llm see llm/agents.py)

.env 파일을 자신의 db, llm, StackStorm 환경에 맞게 작성해주세요