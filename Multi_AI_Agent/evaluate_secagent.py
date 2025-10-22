import argparse
import csv
import json
import os
from typing import Dict, List, Optional

try:
	import urllib.request
except Exception:
	urllib = None  # type: ignore


def clamp_score(value: float, minimum: float = 0.0, maximum: float = 10.0) -> float:
	if value < minimum:
		return minimum
	if value > maximum:
		return maximum
	return value


def ensure_llm_env_defaults() -> None:
	# Default to local Ollama llama4 with deterministic params
	os.environ.setdefault("AAAJ_MODEL", "ollama/llama4")
	os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")
	# Align provider's base url env if missing
	os.environ.setdefault("OPENAI_BASE_URL", os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"))
	# Hint for litellm + ollama providers
	os.environ.setdefault("OLLAMA_API_BASE", os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"))


def _ollama_chat(base_url: str, model: str, system_prompt: str, user_prompt: str) -> Optional[str]:
	if urllib is None:
		return None
	try:
		url = base_url.rstrip("/") + "/api/chat"
		payload = {
			"model": model,
			"messages": [
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": user_prompt},
			],
			"stream": False,
			"options": {"temperature": 0.0, "top_p": 1.0},
		}
		data = json.dumps(payload).encode("utf-8")
		req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
		with urllib.request.urlopen(req, timeout=60) as resp:
			content = resp.read().decode("utf-8")
			obj = json.loads(content)
			# Newer Ollama chat returns {"message": {"role":"assistant","content":"..."}}
			msg = obj.get("message", {}).get("content")
			if not msg:
				# Some variants may return {"response": "..."}
				msg = obj.get("response")
			return msg
	except Exception:
		return None


def call_llm_score(script_text: str, context: Dict[str, str], model_name: Optional[str], repo_overview: Optional[str] = None) -> Optional[Dict[str, object]]:
	try:
		from agent_as_a_judge.llm.provider import LLM
	except Exception:
		LLM = None  # type: ignore

	ensure_llm_env_defaults()

	api_key = os.environ.get("OPENAI_API_KEY")
	ollama_base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
	base_url_env = os.environ.get("OPENAI_BASE_URL")

	# Prefer Ollama when available
	base_url = ollama_base or base_url_env or "http://localhost:11434"
	is_local = True

	model = model_name or os.environ.get("AAAJ_MODEL", "ollama/llama4")

	# Prepare model candidate fallbacks for Ollama (with/without prefix, :latest)
	model_candidates: List[str] = []
	base_name = model.split("/", 1)[1] if model.startswith("ollama/") else model
	model_candidates.extend([
		f"ollama/{base_name}",
		f"ollama/{base_name}:latest",
		base_name,
		f"{base_name}:latest",
	])

	# Common prompts
	system_prompt = (
		"You are an impartial security judge for firewall (iptables) scripts. "
		"Score three aspects from 0 to 10: syntax (grammar/valid options), security (mitigates threat), "
		"optimization (no duplicates/conflicts). Respond with strict JSON only: "
		"{\"syntax\": <0-10>, \"security\": <0-10>, \"optimization\": <0-10>, "
		"\"justification\": {\"syntax\": \"...\", \"security\": \"...\", \"optimization\": \"...\"}}. "
		"Do not include markdown or code fences."
	)
	context_lines = [f"{k}: {v}" for k, v in context.items() if v]
	sections: List[str] = []
	sections.append("Context\n" + "\n".join(context_lines))
	if repo_overview:
		sections.append("Repository\n" + repo_overview)
	sections.append("Script\n" + script_text)
	sections.append("Return JSON only.")
	user_prompt = "\n\n".join(sections)

	# 1) Try direct Ollama chat first (per candidate)
	for model_candidate in model_candidates:
		base_only = model_candidate.split("/", 1)[1] if model_candidate.startswith("ollama/") else model_candidate
		direct = _ollama_chat(base_url, base_only, system_prompt, user_prompt)
		if direct:
			try:
				start = direct.find("{")
				end = direct.rfind("}")
				if start != -1 and end != -1:
					payload = json.loads(direct[start : end + 1])
					syntax = clamp_score(float(payload.get("syntax", 0.0)))
					security = clamp_score(float(payload.get("security", 0.0)))
					optimization = clamp_score(float(payload.get("optimization", 0.0)))
					justification = payload.get("justification", {})
					return {
						"syntax": syntax,
						"security": security,
						"optimization": optimization,
						"justification": justification,
					}
			except Exception:
				pass

	# 2) Fallback to provider path if available
	if LLM is None:
		return None

	for model_candidate in model_candidates:
		try:
			custom_provider = "ollama"
			llm = LLM(
				model=model_candidate,
				api_key=api_key,
				base_url=base_url,
				custom_llm_provider=custom_provider,
				llm_temperature=0.0,
				llm_top_p=1.0,
				llm_timeout=60,
			)
			_resp, content = llm.completion(
				messages=[
					{"role": "system", "content": system_prompt},
					{"role": "user", "content": user_prompt},
				],
				temperature=0.0,
				top_p=1.0,
			)
			start = content.find("{")
			end = content.rfind("}")
			if start == -1 or end == -1:
				continue
			payload = json.loads(content[start : end + 1])
			syntax = clamp_score(float(payload.get("syntax", 0.0)))
			security = clamp_score(float(payload.get("security", 0.0)))
			optimization = clamp_score(float(payload.get("optimization", 0.0)))
			justification = payload.get("justification", {})
			return {
				"syntax": syntax,
				"security": security,
				"optimization": optimization,
				"justification": justification,
			}
		except Exception:
			continue

	return None


def evaluate_llm_only(input_csv: str, output_csv: str, model_name: Optional[str], max_rows: Optional[int] = None, workspace_dir: Optional[str] = None) -> None:
	rows: List[Dict[str, str]] = []
	with open(input_csv, "r", newline="", encoding="utf-8") as f:
		reader = csv.DictReader(f)
		for row in reader:
			rows.append(row)
			if max_rows is not None and len(rows) >= max_rows:
				break

	# Optional: build a brief repository overview to condition the judge
	repo_overview: Optional[str] = None
	if workspace_dir and os.path.isdir(workspace_dir):
		repo_overview_lines: List[str] = []
		max_entries = 80
		count = 0
		for root, dirs, files in os.walk(workspace_dir):
			if count >= max_entries:
				break
			rel_root = os.path.relpath(root, workspace_dir)
			if rel_root == ".":
				rel_root = os.path.basename(os.path.abspath(workspace_dir))
			preview = ", ".join(files[:5]) if files else ""
			repo_overview_lines.append(f"{rel_root}/ -> {preview}")
			count += 1
		repo_overview = "\n".join(repo_overview_lines[:50])

	for row in rows:
		script = row.get("given_script", "") or ""
		context = {
			"attack_type": row.get("attack_type", ""),
			"risk_level": row.get("risk_level", ""),
			"protocol": row.get("protocol", ""),
			"source_ip": row.get("source_ip", ""),
			"dest_ip": row.get("dest_ip", ""),
			"dest_port": row.get("dest_port", ""),
			"action": row.get("action", ""),
			"device_name": row.get("device_name", ""),
		}

		llm_scores = call_llm_score(script, context, model_name, repo_overview)
		if llm_scores is None:
			# If LLM not available, default to zeros with minimal justification
			syntax = 0.0
			security = 0.0
			optimization = 0.0
			justification = {
				"syntax": "LLM unavailable or parsing failed.",
				"security": "LLM unavailable or parsing failed.",
				"optimization": "LLM unavailable or parsing failed.",
			}
		else:
			syntax = float(llm_scores["syntax"])  # already clamped
			security = float(llm_scores["security"])  # already clamped
			optimization = float(llm_scores["optimization"])  # already clamped
			justification = llm_scores.get("justification", {})

		row["syntax_score"] = f"{syntax:.2f}"
		row["security_score"] = f"{security:.2f}"
		row["optimization_score"] = f"{optimization:.2f}"
		row["safety_score"] = row.get("safety_score", "")
		row["_weights"] = "rule=0.00, llm=1.00"
		# Store justification as JSON string (utf-8, no ascii escaping)
		row["justification"] = json.dumps(justification, ensure_ascii=False)

	# Preserve existing headers + new fields (ensuring deterministic order)
	base_fields: List[str] = []
	if rows:
		base_fields = list(rows[0].keys())

	with open(output_csv, "w", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=base_fields)
		writer.writeheader()
		for row in rows:
			writer.writerow(row)


def main() -> None:
	parser = argparse.ArgumentParser(description="Evaluate security scripts using LLM-only scoring (Ollama llama4, deterministic).")
	parser.add_argument("--input", required=True, help="Input CSV path (e.g., secagent.csv)")
	parser.add_argument("--output", required=True, help="Output CSV path")
	parser.add_argument("--model", type=str, default=None, help="LLM model name (default: ollama/llama4)")
	parser.add_argument("--max-rows", type=int, default=None, help="Max rows to evaluate (optional)")
	parser.add_argument("--workspace-dir", type=str, default=None, help="Repository/workspace directory to include as evidence (optional)")
	args = parser.parse_args()

	ensure_llm_env_defaults()
	model_name = args.model or os.environ.get("AAAJ_MODEL", "ollama/llama4:latest")
	os.environ.setdefault("DEFAULT_LLM", model_name)

	evaluate_llm_only(args.input, args.output, model_name, args.max_rows, args.workspace_dir)
	print(f"[Eval-LLM] Done. Wrote: {args.output}")


if __name__ == "__main__":
	main()



