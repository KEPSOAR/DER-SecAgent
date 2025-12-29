# Agent-as-a-Judge implementation for evaluating security scripts
import os
import sys
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# Add Agent-as-a-Judge library path
sys.path.append('/root/Multi_AI_Agent/agent-as-a-judge')

# Ollama connection and timeout configuration — reinforced settings
os.environ["LITELLM_REQUEST_TIMEOUT"] = "600"  # increased to 10 minutes
os.environ["OLLAMA_REQUEST_TIMEOUT"] = "600"
os.environ["LITELLM_DROP_PARAMS"] = "true"
os.environ["LITELLM_LOG"] = "ERROR"  # adjust log level

# LiteLLM timeout — configured via environment variables only
print("⚠️ Timeout configured via environment variables: 600 seconds")

# Ollama model (use a lighter/faster model)
DEFAULT_OLLAMA_MODEL = "llama3.2:1b"  # faster model
DEFAULT_MODEL = os.getenv("DEFAULT_LLM", f"ollama/{DEFAULT_OLLAMA_MODEL}")

from agent_as_a_judge.agent import JudgeAgent
from agent_as_a_judge.config import AgentConfig
from kepsoar.graph.states import soar_input, attack_type

@dataclass
class SecurityJudgeResult:
    """Security script evaluation result (1–10 scale)"""
    syntax_score: int = 0  # 1–10 points
    security_score: int = 0  # 1–10 points
    safety_score: int = 0  # 1–10 points
    optimization_score: int = 0  # 1–10 points
    overall_score: float = 0.0  # average score
    syntax_reason: str = ""
    security_reason: str = ""
    safety_reason: str = ""
    optimization_reason: str = ""
    detailed_feedback: str = ""
    judge_time: float = 0.0
    judge_cost: float = 0.0

    @property
    def syntax_satisfied(self) -> bool:
        """Property kept for backward compatibility"""
        return self.syntax_score >= 6

    @property
    def security_satisfied(self) -> bool:
        """Property kept for backward compatibility"""
        return self.security_score >= 6

    @property
    def safety_satisfied(self) -> bool:
        """Property kept for backward compatibility"""
        return self.safety_score >= 6

    @property
    def optimization_satisfied(self) -> bool:
        """Property kept for backward compatibility"""
        return self.optimization_score >= 6

    @property
    def overall_satisfied(self) -> bool:
        """Property kept for backward compatibility"""
        return self.overall_score >= 6.0

class SecurityScriptJudge:
    """
    Security script evaluation system using the official Agent-as-a-Judge framework
    """

    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="security_judge_"))
        self.judge_dir = self.temp_dir / "judge"
        self.judge_dir.mkdir(parents=True, exist_ok=True)

        # Check environment variables and set defaults
        if not os.getenv("DEFAULT_LLM"):
            os.environ["DEFAULT_LLM"] = DEFAULT_MODEL
        if not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = "not-needed-for-ollama"

        # Attack-specific evaluation criteria (1–10 scale)
        self.attack_criteria = {
            attack_type.DoS: {
                "syntax": "Evaluate iptables command syntax correctness on a 1–10 scale. (1: severe syntax errors, 5: basic syntax correct, 10: perfect syntax and structure)",
                "security": "Evaluate DoS mitigation effectiveness on a 1–10 scale. (1: ineffective, 5: basic mitigation, 10: excellent DoS defense)",
                "safety": "Evaluate protection of legitimate traffic and service stability on a 1–10 scale. (1: high outage risk, 5: basic safety, 10: excellent safety)",
                "optimization": "Evaluate rule efficiency and optimization on a 1–10 scale. (1: very inefficient, 5: basic efficiency, 10: highly optimized)"
            },
            attack_type.Probe: {
                "syntax": "Evaluate iptables command syntax correctness on a 1–10 scale. (1: severe syntax errors, 5: basic syntax correct, 10: perfect syntax and structure)",
                "security": "Evaluate Probe/scanning mitigation effectiveness on a 1–10 scale. (1: ineffective, 5: basic mitigation, 10: excellent scanning defense)",
                "safety": "Evaluate protection of legitimate service access on a 1–10 scale. (1: blocks normal services, 5: basic safety, 10: excellent service protection)",
                "optimization": "Evaluate rule efficiency and optimization on a 1–10 scale. (1: very inefficient, 5: basic efficiency, 10: highly optimized)"
            },
            attack_type.BruteForce: {
                "syntax": "Evaluate iptables command syntax correctness on a 1–10 scale. (1: severe syntax errors, 5: basic syntax correct, 10: perfect syntax and structure)",
                "security": "Evaluate brute-force mitigation effectiveness on a 1–10 scale. (1: ineffective, 5: basic mitigation, 10: excellent brute-force defense)",
                "safety": "Evaluate protection of legitimate user access on a 1–10 scale. (1: blocks legitimate users, 5: basic safety, 10: excellent user protection)",
                "optimization": "Evaluate rate-limiting rule efficiency on a 1–10 scale. (1: very inefficient, 5: basic efficiency, 10: highly optimized)"
            },
            attack_type.MITM: {
                "syntax": "Evaluate iptables command syntax correctness on a 1–10 scale. (1: severe syntax errors, 5: basic syntax correct, 10: perfect syntax and structure)",
                "security": "Evaluate MITM defense effectiveness on a 1–10 scale. (1: ineffective, 5: basic defense, 10: excellent MITM defense)",
                "safety": "Evaluate protection of legitimate connections on a 1–10 scale. (1: blocks normal connections, 5: basic safety, 10: excellent connection protection)",
                "optimization": "Evaluate rule efficiency and optimization on a 1–10 scale. (1: very inefficient, 5: basic efficiency, 10: highly optimized)"
            },
            attack_type.R2L: {
                "syntax": "Evaluate iptables command syntax correctness on a 1–10 scale. (1: severe syntax errors, 5: basic syntax correct, 10: perfect syntax and structure)",
                "security": "Evaluate remote access attack mitigation effectiveness (R2L) on a 1–10 scale. (1: ineffective, 5: basic mitigation, 10: excellent defense)",
                "safety": "Evaluate protection of legitimate remote access on a 1–10 scale. (1: blocks normal access, 5: basic safety, 10: excellent protection)",
                "optimization": "Evaluate access control rule efficiency on a 1–10 scale. (1: very inefficient, 5: basic efficiency, 10: highly optimized)"
            },
            attack_type.U2R: {
                "syntax": "Evaluate iptables command syntax correctness on a 1–10 scale. (1: severe syntax errors, 5: basic syntax correct, 10: perfect syntax and structure)",
                "security": "Evaluate privilege escalation (U2R) defense effectiveness on a 1–10 scale. (1: ineffective, 5: basic defense, 10: excellent U2R defense)",
                "safety": "Evaluate protection of legitimate admin access on a 1–10 scale. (1: blocks admin access, 5: basic safety, 10: excellent protection)",
                "optimization": "Evaluate efficiency of role/privilege-based access controls on a 1–10 scale. (1: very inefficient, 5: basic efficiency, 10: highly optimized)"
            }
        }

    def create_temp_workspace(self, script: str, state: soar_input) -> Path:
        """Create a temporary workspace for evaluation"""
        workspace_dir = self.temp_dir / "workspace"
        workspace_dir.mkdir(exist_ok=True)

        # Create script file (.txt so Agent-as-a-Judge can read it)
        script_file = workspace_dir / "security_script.txt"
        script_file.write_text(f"# Generated security script\n{script}")

        # Create context file
        context_file = workspace_dir / "context.json"
        context_data = {
            "attack_type": state["attack_type"].value,
            "source_ip": state["source_ip"],
            "dest_ip": state["dest_ip"],
            "dest_port": state["dest_port"],
            "protocol": state["protocol"],
            "device_ip": state["device_ip"],
            "device_name": state["device_name"]
        }
        context_file.write_text(json.dumps(context_data, indent=2))

        # Create README file
        readme_file = workspace_dir / "README.md"
        readme_content = f"""# Security Script Evaluation

## Context
- Attack Type: {state["attack_type"].value}
- Source IP: {state["source_ip"]}
- Destination IP: {state["dest_ip"]}
- Destination Port: {state["dest_port"]}
- Protocol: {state["protocol"]}

## Script (security_script.txt)
The iptables security script to be evaluated.

## Evaluation Criteria (1-10 point scale)
This script will be evaluated on:
1. Syntax correctness (1–10)
2. Security effectiveness (1–10)
3. Safety impact (1–10)
4. Optimization level (1–10)

Please provide scores in the format: "Score: X"
"""
        readme_file.write_text(readme_content)

        return workspace_dir

    def create_instance_file(self, script: str, state: soar_input) -> Path:
        """Create evaluation instance file"""
        attack_type_val = state["attack_type"]
        criteria = self.attack_criteria.get(attack_type_val, self.attack_criteria[attack_type.DoS])

        instance_data = {
            "name": f"security_script_{attack_type_val.value}",
            "query": f"Evaluate the security script for {attack_type_val.value} attack mitigation using 1-10 point scale",
            "requirements": [
                {
                    "criteria": f"Syntax evaluation: {criteria['syntax']} Answer strictly in the format 'Score: X'.",
                    "category": "syntax"
                },
                {
                    "criteria": f"Security evaluation: {criteria['security']} Answer strictly in the format 'Score: X'.",
                    "category": "security"
                },
                {
                    "criteria": f"Safety evaluation: {criteria['safety']} Answer strictly in the format 'Score: X'.",
                    "category": "safety"
                },
                {
                    "criteria": f"Optimization evaluation: {criteria['optimization']} Answer strictly in the format 'Score: X'.",
                    "category": "optimization"
                }
            ]
        }

        instance_file = self.judge_dir / "instance.json"
        instance_file.write_text(json.dumps(instance_data, indent=2))
        return instance_file

    def judge_script(self, script: str, state: soar_input) -> SecurityJudgeResult:
        """
        Security script evaluation using the official Agent-as-a-Judge
        """
        try:
            # Create temporary workspace and instance
            workspace_dir = self.create_temp_workspace(script, state)
            instance_file = self.create_instance_file(script, state)

            # Agent-as-a-Judge configuration
            config = AgentConfig(
                include_dirs=[""],
                exclude_dirs=["__pycache__", ".git"],
                exclude_files=[".DS_Store"],
                setting="gray_box",  # code accessible
                planning="efficient (no planning)"  # efficient evaluation
            )

            # Create Judge Agent and run evaluation
            judge = JudgeAgent(
                workspace=workspace_dir,
                instance=instance_file,
                judge_dir=self.judge_dir,
                config=config
            )

            # Strengthen timeout configuration on Judge's LLM instance
            if hasattr(judge, 'llm'):
                if hasattr(judge.llm, 'llm_timeout'):
                    judge.llm.llm_timeout = 600  # 10-minute timeout
                if hasattr(judge.llm, 'timeout'):
                    judge.llm.timeout = 600
                if hasattr(judge.llm, 'request_timeout'):
                    judge.llm.request_timeout = 600
                # Force apply timeouts by re-initializing completion function
                if hasattr(judge.llm, '_initialize_completion_function'):
                    judge.llm.llm_timeout = 600
                    judge.llm._initialize_completion_function()

            # Run evaluation
            judge.judge_anything()

            # Analyze results
            result = self._analyze_judge_results(judge.judge_stats)

            return result

        except Exception as e:
            print(f"Error during Judge evaluation: {e}")
            return SecurityJudgeResult(
                detailed_feedback=f"Error during evaluation: {str(e)}"
            )
        finally:
            # Clean up temporary files
            self._cleanup_temp_files()

    def _analyze_judge_results(self, judge_stats: List[Dict]) -> SecurityJudgeResult:
        """Analyze Judge results (1–10 scale)"""
        import re

        result = SecurityJudgeResult()

        # Store scores and reasons per category
        category_scores = {}
        category_reasons = {}
        total_cost = 0.0
        total_time = 0.0
        feedback_parts = []

        for stat in judge_stats:
            criteria = stat["criteria"]
            satisfied = stat["satisfied"]
            llm_stats = stat.get("llm_stats", {})

            # Extract score from LLM response
            reason_text = ""
            if isinstance(llm_stats.get("reason"), list) and llm_stats["reason"]:
                reason_text = str(llm_stats["reason"][0])
            elif isinstance(llm_stats.get("reason"), str):
                reason_text = llm_stats["reason"]

            # Decide category
            if "syntax" in criteria.lower():
                category = "syntax"
            elif "security" in criteria.lower():
                category = "security"
            elif "safety" in criteria.lower():
                category = "safety"
            elif "optimization" in criteria.lower():
                category = "optimization"
            else:
                category = "general"

            # Extract score (try multiple patterns)
            score = 0
            score_patterns = [
                r"Score[:\s]*(\d+)",
                r"rating[:\s]*(\d+)",
                r"(\d+)/10",
                r"(\d+)\s*out\s*of\s*10"
            ]

            for pattern in score_patterns:
                match = re.search(pattern, reason_text, re.IGNORECASE)
                if match:
                    try:
                        extracted_score = int(match.group(1))
                        if 1 <= extracted_score <= 10:
                            score = extracted_score
                            break
                    except (ValueError, IndexError):
                        continue

            # If no explicit score found, infer from 'satisfied'
            if score == 0:
                score = 7 if satisfied else 3

            category_scores[category] = score
            category_reasons[category] = reason_text

            # Accumulate cost and time
            total_cost += llm_stats.get("cost", 0.0)
            total_time += llm_stats.get("inference_time", 0.0)

            # Collect feedback
            feedback_parts.append(f"**{category.upper()}**: {score}/10\n{reason_text}")

        # Set scores to result
        result.syntax_score = category_scores.get("syntax", 0)
        result.security_score = category_scores.get("security", 0)
        result.safety_score = category_scores.get("safety", 0)
        result.optimization_score = category_scores.get("optimization", 0)

        # Set individual reasons
        result.syntax_reason = category_reasons.get("syntax", "No evaluation")
        result.security_reason = category_reasons.get("security", "No evaluation")
        result.safety_reason = category_reasons.get("safety", "No evaluation")
        result.optimization_reason = category_reasons.get("optimization", "No evaluation")

        # Compute overall average score
        valid_scores = [score for score in [result.syntax_score, result.security_score,
                                          result.safety_score, result.optimization_score] if score > 0]
        result.overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

        result.detailed_feedback = "\n\n".join(feedback_parts)
        result.judge_time = total_time
        result.judge_cost = total_cost

        return result

    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        import shutil
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error while cleaning up temporary files: {e}")

# Singleton instance
security_judge = SecurityScriptJudge()

