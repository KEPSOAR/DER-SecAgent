## DER-SecAgent: Multi-Agent (kepsoar)

> Python scripts for a LangGraph-based multi-agent pipeline.

---

## Dependencies

- **langchain**
- **langchain-community**
- **langchain-ollama**
- **langgraph**
- **mysql-connector-python** (not supported yet)
- **google**
- **cloud-sql-python-connector**
- **sqlalchemy**
- **pymysql**

---

## System Requirements

- **ollama** installed with models stored locally
  - To change the LLM configuration, see `kepsoar/llm/agents.py`.

---

## Setup

### 1) Install Python dependencies

```bash
pip install -r Multi_AI_Agent/requirements.txt
```

### 2) Configure environment

- Create a `.env` file to fit your DB, LLM, and StackStorm settings.

### 3) Entry points

- See `Multi_AI_Agent/main.py` and `Multi_AI_Agent/kepsoar/graph/*.py` for how the agents and graphs are composed and executed.
