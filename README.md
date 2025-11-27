<p align="center">
  <img src="./assets/logo.png" alt="DER-SecAgent Logo" width="600px" />
</p>



# DER-SecAgent

> **DER-SecAgent: A Multi-Agent based Cybersecurity Framework for Distributed Energy Resources**  
> AI agent to assist with cybersecurity for DER and power-system OT/ICS.

**DER-SecAgent** uses domain-adapted language models to help with:

- Security assessments for solar PV, ESS, inverters/PCS, EV chargers, EMS/DERMS, etc.
- Threat and risk analysis for OT/ICS architectures
- Drafting security reports, checklists, and action plans

This repository is intended as a **research / prototype framework**, not a production-ready security product.

---

## Key Features

- 🔐 **DER / OT Security–Specialized LLM Agent**
  - Focus on DER equipment (PV, ESS, PCS/inverters, EV chargers, gateways, EMS/DERMS)
  - OT network / DMZ / firewall / remote access security reasoning

- 📄 **PDF → SFT Dataset Pipeline (Concept)**
  - Ingest security guidelines, checklists, and reports in PDF form
  - Clean and convert them into instruction–response pairs (SFT dataset) for training

- 🧠 **Multi-Agent Architecture (Planned)**
  - Separation between:
    - “Analysis / report agent” (text generation, explanation, summaries)
    - “Policy / action agent” (rule-based logic, playbooks, orchestration)
  - Future examples using LangGraph or similar multi-agent frameworks

- ☁️ **Hugging Face & PEFT Integration**
  - LoRA / QLoRA training scripts (planned)
  - Easy integration with the published DER-SecAgent adapter on Hugging Face:
    - [`MyeongHaHwang/DER-SecAgent-LLama3.2-3B-Inst-SFT`](https://huggingface.co/MyeongHaHwang/DER-SecAgent-LLama3.2-3B-Inst-SFT)

---

## Architecture Overview

High-level layers:

1. **Document Layer – Security Knowledge Ingestion**
   - Collect DER / OT / ICS security PDFs (guidelines, manuals, audit checklists, case reports)
   - Extract and clean text
   - Turn content into instruction–response pairs for supervised fine-tuning (SFT)

2. **Model Layer – Domain-Specific LLM**
   - Base model: `meta-llama/Llama-3.2-3B-Instruct`
   - LoRA / QLoRA SFT to create a DER security–specialized adapter
   - Adapter published on Hugging Face for reuse

3. **Agent Layer – Security Copilot / Orchestrator**
   - “Security analysis & reporting” agent:
     - Q&A, explanations, summaries, report drafts
   - (Planned) “Policy & action” agent:
     - Maps findings to recommended controls, playbooks, or automation steps
   - Future multi-agent flows (e.g., LangGraph) to coordinate between agents

---

## Getting Started

### 1. Requirements

Typical environment (adjust as needed):

- Python 3.10+
- PyTorch 2.x
- `transformers` (e.g., ≥ 4.43)
- `peft` (e.g., 0.17.1)
- Optional: `bitsandbytes` for 4-bit / 8-bit quantization
- GPU with ~24–40GB VRAM recommended for training / finetuning

### 2. Installation

```bash
git clone https://github.com/KEPSOAR/DER-SecAgent.git
cd DER-SecAgent

# Example (adapt to the actual repo contents)
pip install -r requirements.txt

```

## Cite Us

If you use this repository or the DER-SecAgent LoRA adapter in your research or projects, please cite:

```bibtex
@misc{hwang2025dersecagent,
  title        = {DER-SecAgent: A Multi-Agent based Cybersecurity Framework for Distributed Energy Resources},
  author       = {Hwang, MyeongHa, Kyungmin Kim, Hyeongu Kim, Yoojin Kwon, Sungho Lee},
  year         = {2025},
  howpublished = {\url{https://github.com/KEPSOAR/DER-SecAgent}},
  note         = {Includes the DER-SecAgent-LLama3.2-3B-Inst-SFT LoRA adapter.}
}
---
