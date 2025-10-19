# 보안 스크립트 평가를 위한 Agent-as-a-Judge 구현
import os
import sys
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# Agent-as-a-Judge 라이브러리 경로 추가
sys.path.append('/root/Multi_AI_Agent/agent-as-a-judge')

# Ollama 연결 및 타임아웃 설정 - 강화된 설정
os.environ["LITELLM_REQUEST_TIMEOUT"] = "600"  # 10분으로 증가
os.environ["OLLAMA_REQUEST_TIMEOUT"] = "600"
os.environ["LITELLM_DROP_PARAMS"] = "true"
os.environ["LITELLM_LOG"] = "ERROR"  # 로그 레벨 조정

# LiteLLM 타임아웃 설정 - 환경변수만 사용
print("⚠️ 환경변수로 타임아웃 설정: 600초")

# Ollama 모델 설정 (더 가벼운 모델로 변경)
DEFAULT_OLLAMA_MODEL = "llama3.2:1b"  # 더 빠른 모델 사용
DEFAULT_MODEL = os.getenv("DEFAULT_LLM", f"ollama/{DEFAULT_OLLAMA_MODEL}")

from agent_as_a_judge.agent import JudgeAgent
from agent_as_a_judge.config import AgentConfig
from kepsoar.graph.states import soar_input, attack_type

@dataclass
class SecurityJudgeResult:
    """보안 스크립트 평가 결과 (1-10점 스케일)"""
    syntax_score: int = 0  # 1-10점
    security_score: int = 0  # 1-10점
    safety_score: int = 0  # 1-10점
    optimization_score: int = 0  # 1-10점
    overall_score: float = 0.0  # 평균 점수
    syntax_reason: str = ""
    security_reason: str = ""
    safety_reason: str = ""
    optimization_reason: str = ""
    detailed_feedback: str = ""
    judge_time: float = 0.0
    judge_cost: float = 0.0

    @property
    def syntax_satisfied(self) -> bool:
        """하위 호환성을 위한 속성"""
        return self.syntax_score >= 6

    @property
    def security_satisfied(self) -> bool:
        """하위 호환성을 위한 속성"""
        return self.security_score >= 6

    @property
    def safety_satisfied(self) -> bool:
        """하위 호환성을 위한 속성"""
        return self.safety_score >= 6

    @property
    def optimization_satisfied(self) -> bool:
        """하위 호환성을 위한 속성"""
        return self.optimization_score >= 6

    @property
    def overall_satisfied(self) -> bool:
        """하위 호환성을 위한 속성"""
        return self.overall_score >= 6.0

class SecurityScriptJudge:
    """
    공식 Agent-as-a-Judge 프레임워크를 사용한 보안 스크립트 평가 시스템
    """

    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="security_judge_"))
        self.judge_dir = self.temp_dir / "judge"
        self.judge_dir.mkdir(parents=True, exist_ok=True)

        # 환경변수 설정 확인 및 기본값 설정
        if not os.getenv("DEFAULT_LLM"):
            os.environ["DEFAULT_LLM"] = DEFAULT_MODEL
        if not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = "not-needed-for-ollama"

        # 공격 유형별 특화 평가 기준 (1-10점 스케일)
        self.attack_criteria = {
            attack_type.DoS: {
                "syntax": "iptables 명령어 문법의 정확성을 1-10점으로 평가하세요. (1: 심각한 구문 오류, 5: 기본 문법은 맞음, 10: 완벽한 문법과 구조)",
                "security": "DoS 공격 차단 효과성을 1-10점으로 평가하세요. (1: 전혀 효과 없음, 5: 기본적 차단, 10: 완벽한 DoS 방어)",
                "safety": "정상 트래픽 보호와 서비스 안정성을 1-10점으로 평가하세요. (1: 서비스 장애 위험, 5: 기본 안전성, 10: 완벽한 안전성)",
                "optimization": "규칙의 효율성과 최적화를 1-10점으로 평가하세요. (1: 매우 비효율적, 5: 기본적 효율성, 10: 최적화된 구조)"
            },
            attack_type.Probe: {
                "syntax": "iptables 명령어 문법의 정확성을 1-10점으로 평가하세요. (1: 심각한 구문 오류, 5: 기본 문법은 맞음, 10: 완벽한 문법과 구조)",
                "security": "Probe 공격 차단 효과성을 1-10점으로 평가하세요. (1: 전혀 효과 없음, 5: 기본적 차단, 10: 완벽한 스캐닝 방어)",
                "safety": "합법적 서비스 접근 보호를 1-10점으로 평가하세요. (1: 정상 서비스 차단, 5: 기본 안전성, 10: 완벽한 서비스 보호)",
                "optimization": "규칙의 효율성과 최적화를 1-10점으로 평가하세요. (1: 매우 비효율적, 5: 기본적 효율성, 10: 최적화된 구조)"
            },
            attack_type.BruteForce: {
                "syntax": "iptables 명령어 문법의 정확성을 1-10점으로 평가하세요. (1: 심각한 구문 오류, 5: 기본 문법은 맞음, 10: 완벽한 문법과 구조)",
                "security": "무차별 대입 공격 차단 효과성을 1-10점으로 평가하세요. (1: 전혀 효과 없음, 5: 기본적 차단, 10: 완벽한 브루트포스 방어)",
                "safety": "정상 사용자 접근 보호를 1-10점으로 평가하세요. (1: 정상 사용자 차단, 5: 기본 안전성, 10: 완벽한 사용자 보호)",
                "optimization": "Rate limiting 규칙의 효율성을 1-10점으로 평가하세요. (1: 매우 비효율적, 5: 기본적 효율성, 10: 최적화된 구조)"
            },
            attack_type.MITM: {
                "syntax": "iptables 명령어 문법의 정확성을 1-10점으로 평가하세요. (1: 심각한 구문 오류, 5: 기본 문법은 맞음, 10: 완벽한 문법과 구조)",
                "security": "중간자 공격 방어 효과성을 1-10점으로 평가하세요. (1: 전혀 효과 없음, 5: 기본적 방어, 10: 완벽한 MITM 방어)",
                "safety": "합법적 연결 보호를 1-10점으로 평가하세요. (1: 정상 연결 차단, 5: 기본 안전성, 10: 완벽한 연결 보호)",
                "optimization": "보안 규칙의 효율성을 1-10점으로 평가하세요. (1: 매우 비효율적, 5: 기본적 효율성, 10: 최적화된 구조)"
            },
            attack_type.R2L: {
                "syntax": "iptables 명령어 문법의 정확성을 1-10점으로 평가하세요. (1: 심각한 구문 오류, 5: 기본 문법은 맞음, 10: 완벽한 문법과 구조)",
                "security": "원격 접근 공격 차단 효과성을 1-10점으로 평가하세요. (1: 전혀 효과 없음, 5: 기본적 차단, 10: 완벽한 R2L 방어)",
                "safety": "합법적 원격 접근 보호를 1-10점으로 평가하세요. (1: 정상 접근 차단, 5: 기본 안전성, 10: 완벽한 접근 보호)",
                "optimization": "접근 제어 규칙의 효율성을 1-10점으로 평가하세요. (1: 매우 비효율적, 5: 기본적 효율성, 10: 최적화된 구조)"
            },
            attack_type.U2R: {
                "syntax": "iptables 명령어 문법의 정확성을 1-10점으로 평가하세요. (1: 심각한 구문 오류, 5: 기본 문법은 맞음, 10: 완벽한 문법과 구조)",
                "security": "권한 상승 공격 방어 효과성을 1-10점으로 평가하세요. (1: 전혀 효과 없음, 5: 기본적 방어, 10: 완벽한 U2R 방어)",
                "safety": "정상적 관리자 접근 보호를 1-10점으로 평가하세요. (1: 관리자 접근 차단, 5: 기본 안전성, 10: 완벽한 관리자 보호)",
                "optimization": "권한별 접근 제어의 효율성을 1-10점으로 평가하세요. (1: 매우 비효율적, 5: 기본적 효율성, 10: 최적화된 구조)"
            }
        }

    def create_temp_workspace(self, script: str, state: soar_input) -> Path:
        """평가를 위한 임시 워크스페이스 생성"""
        workspace_dir = self.temp_dir / "workspace"
        workspace_dir.mkdir(exist_ok=True)

        # 스크립트 파일 생성 (.txt 형식으로 변경하여 Agent-as-a-Judge가 읽을 수 있도록)
        script_file = workspace_dir / "security_script.txt"
        script_file.write_text(f"# Generated security script\n{script}")

        # 컨텍스트 정보 파일 생성
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

        # README 파일 생성
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
1. Syntax correctness (1-10점)
2. Security effectiveness (1-10점)
3. Safety impact (1-10점)
4. Optimization level (1-10점)

Please provide scores in format: "점수: X점"
"""
        readme_file.write_text(readme_content)

        return workspace_dir

    def create_instance_file(self, script: str, state: soar_input) -> Path:
        """평가 인스턴스 파일 생성"""
        attack_type_val = state["attack_type"]
        criteria = self.attack_criteria.get(attack_type_val, self.attack_criteria[attack_type.DoS])

        instance_data = {
            "name": f"security_script_{attack_type_val.value}",
            "query": f"Evaluate the security script for {attack_type_val.value} attack mitigation using 1-10 point scale",
            "requirements": [
                {
                    "criteria": f"문법 평가: {criteria['syntax']} 반드시 '점수: X점' 형식으로 답변하세요.",
                    "category": "syntax"
                },
                {
                    "criteria": f"보안 평가: {criteria['security']} 반드시 '점수: X점' 형식으로 답변하세요.",
                    "category": "security"
                },
                {
                    "criteria": f"안전성 평가: {criteria['safety']} 반드시 '점수: X점' 형식으로 답변하세요.",
                    "category": "safety"
                },
                {
                    "criteria": f"최적화 평가: {criteria['optimization']} 반드시 '점수: X점' 형식으로 답변하세요.",
                    "category": "optimization"
                }
            ]
        }

        instance_file = self.judge_dir / "instance.json"
        instance_file.write_text(json.dumps(instance_data, indent=2))
        return instance_file

    def judge_script(self, script: str, state: soar_input) -> SecurityJudgeResult:
        """
        공식 Agent-as-a-Judge를 사용한 보안 스크립트 평가
        """
        try:
            # 임시 워크스페이스 및 인스턴스 생성
            workspace_dir = self.create_temp_workspace(script, state)
            instance_file = self.create_instance_file(script, state)

            # Agent-as-a-Judge 설정
            config = AgentConfig(
                include_dirs=[""],
                exclude_dirs=["__pycache__", ".git"],
                exclude_files=[".DS_Store"],
                setting="gray_box",  # 코드 접근 가능
                planning="efficient (no planning)"  # 효율적인 평가
            )

            # Judge Agent 생성 및 평가 실행
            judge = JudgeAgent(
                workspace=workspace_dir,
                instance=instance_file,
                judge_dir=self.judge_dir,
                config=config
            )

            # Judge의 LLM 인스턴스에 타임아웃 설정 강화
            if hasattr(judge, 'llm'):
                if hasattr(judge.llm, 'llm_timeout'):
                    judge.llm.llm_timeout = 600  # 10분 타임아웃
                if hasattr(judge.llm, 'timeout'):
                    judge.llm.timeout = 600
                if hasattr(judge.llm, 'request_timeout'):
                    judge.llm.request_timeout = 600
                # completion 함수 재생성으로 타임아웃 강제 적용
                if hasattr(judge.llm, '_initialize_completion_function'):
                    judge.llm.llm_timeout = 600
                    judge.llm._initialize_completion_function()

            # 평가 실행
            judge.judge_anything()

            # 결과 분석
            result = self._analyze_judge_results(judge.judge_stats)

            return result

        except Exception as e:
            print(f"Judge 평가 중 오류 발생: {e}")
            return SecurityJudgeResult(
                detailed_feedback=f"평가 중 오류 발생: {str(e)}"
            )
        finally:
            # 임시 파일 정리
            self._cleanup_temp_files()

    def _analyze_judge_results(self, judge_stats: List[Dict]) -> SecurityJudgeResult:
        """Judge 평가 결과 분석 (1-10점 스케일)"""
        import re

        result = SecurityJudgeResult()

        # 각 카테고리별 점수와 이유 저장
        category_scores = {}
        category_reasons = {}
        total_cost = 0.0
        total_time = 0.0
        feedback_parts = []

        for stat in judge_stats:
            criteria = stat["criteria"]
            satisfied = stat["satisfied"]
            llm_stats = stat.get("llm_stats", {})

            # LLM 응답에서 점수 추출
            reason_text = ""
            if isinstance(llm_stats.get("reason"), list) and llm_stats["reason"]:
                reason_text = str(llm_stats["reason"][0])
            elif isinstance(llm_stats.get("reason"), str):
                reason_text = llm_stats["reason"]

            # 카테고리 결정
            if "문법" in criteria or "syntax" in criteria.lower():
                category = "syntax"
            elif "보안" in criteria or "security" in criteria.lower():
                category = "security"
            elif "안전" in criteria or "safety" in criteria.lower():
                category = "safety"
            elif "최적화" in criteria or "optimization" in criteria.lower():
                category = "optimization"
            else:
                category = "general"

            # 점수 추출 (다양한 패턴 시도)
            score = 0
            score_patterns = [
                r"점수[:\s]*(\d+)점",
                r"(\d+)점",
                r"점수[:\s]*(\d+)",
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

            # 점수를 찾지 못한 경우 satisfied 여부로 추정
            if score == 0:
                score = 7 if satisfied else 3

            category_scores[category] = score
            category_reasons[category] = reason_text

            # 비용 및 시간 누적
            total_cost += llm_stats.get("cost", 0.0)
            total_time += llm_stats.get("inference_time", 0.0)

            # 피드백 수집
            feedback_parts.append(f"**{category.upper()}**: {score}점/10점\n{reason_text}")

        # 결과에 점수 설정
        result.syntax_score = category_scores.get("syntax", 0)
        result.security_score = category_scores.get("security", 0)
        result.safety_score = category_scores.get("safety", 0)
        result.optimization_score = category_scores.get("optimization", 0)

        # 개별 이유 설정
        result.syntax_reason = category_reasons.get("syntax", "평가 없음")
        result.security_reason = category_reasons.get("security", "평가 없음")
        result.safety_reason = category_reasons.get("safety", "평가 없음")
        result.optimization_reason = category_reasons.get("optimization", "평가 없음")

        # 전체 평균 점수 계산
        valid_scores = [score for score in [result.syntax_score, result.security_score,
                                          result.safety_score, result.optimization_score] if score > 0]
        result.overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

        result.detailed_feedback = "\n\n".join(feedback_parts)
        result.judge_time = total_time
        result.judge_cost = total_cost

        return result

    def _cleanup_temp_files(self):
        """임시 파일 정리"""
        import shutil
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"임시 파일 정리 중 오류: {e}")

# 싱글톤 인스턴스
security_judge = SecurityScriptJudge()

