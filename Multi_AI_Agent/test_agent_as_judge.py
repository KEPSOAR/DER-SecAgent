#!/usr/bin/env python3
"""
Agent-as-a-Judge 보안 스크립트 평가 테스트
데이터베이스에서 히스토리 데이터를 가져와서 평가
"""
import os
import sys
from pathlib import Path
# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from kepsoar.llm.security_judge import security_judge
from kepsoar.graph.states import soar_input, attack_type
from kepsoar.db.db_connect import fetch_history_storage_by_key
from kepsoar.utils.parser import parse_from_history
from datetime import datetime

def load_history_data(history_id: int):
    """데이터베이스에서 히스토리 데이터를 가져와서 파싱"""
    try:
        # 데이터베이스에서 히스토리 데이터 조회
        history_data = fetch_history_storage_by_key(history_id)

        if not history_data:
            print(f"❌ ID {history_id}에 해당하는 히스토리 데이터를 찾을 수 없습니다.")
            return None, None

        print(f"✅ 데이터베이스에서 히스토리 ID {history_id} 데이터 로드 완료")
        print(f"📊 조회된 데이터 수: {len(history_data)}개")

        # 첫 번째 레코드 정보 출력
        if history_data:
            record = history_data[0]
            print(f"📝 공격 유형: {record.get('attack_type', 'Unknown')}")
            print(f"🕐 이벤트 시간: {record.get('event_time', 'Unknown')}")
            print(f"🔧 실행된 스크립트: {record.get('executed_script', 'None')}")

        # 히스토리 데이터를 soar_input 형태로 파싱
        parsed_state = parse_from_history(history_data)

        # 실행된 스크립트 추출 (executed_script 필드)
        script = history_data[0].get('executed_script', '') if history_data else ''

        return parsed_state, script

    except Exception as e:
        print(f"❌ 데이터베이스에서 데이터 로드 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_security_judge(history_id: int):
    """Agent-as-a-Judge 테스트 (데이터베이스에서 데이터 로드)"""

    print(f"\n🤖 Agent-as-a-Judge 보안 스크립트 평가 테스트")
    print(f"📊 히스토리 ID: {history_id}")
    print("=" * 80)

    # 데이터베이스에서 데이터 로드
    state_data, script = load_history_data(history_id)

    if not state_data or not script:
        print("❌ 테스트에 필요한 데이터를 로드할 수 없습니다.")
        return

    print(f"📝 평가할 스크립트:")
    print(f"```bash")
    print(script)
    print(f"```")
    print(f"\n📋 상태 정보:")
    print(f"  🎯 공격 유형: {state_data['attack_type'].value}")
    print(f"  🌐 소스 IP: {state_data['source_ip']}")
    print(f"  🎯 대상 IP: {state_data['dest_ip']}")
    print(f"  🔌 대상 포트: {state_data['dest_port']}")
    print(f"  📡 프로토콜: {state_data['protocol']}")

    # Judge 평가 실행
    try:
        print("🔍 Agent-as-a-Judge 평가 시작...")
        result = security_judge.judge_script(script, state_data)

        print("\n📊 평가 결과 (1-10점 스케일):")
        print(f"  📝 Syntax: {result.syntax_score}점/10점 {'✅' if result.syntax_satisfied else '❌'}")
        print(f"  🛡️ Security: {result.security_score}점/10점 {'✅' if result.security_satisfied else '❌'}")
        print(f"  🔒 Safety: {result.safety_score}점/10점 {'✅' if result.safety_satisfied else '❌'}")
        print(f"  ⚡ Optimization: {result.optimization_score}점/10점 {'✅' if result.optimization_satisfied else '❌'}")
        print(f"  📊 Overall: {result.overall_score:.1f}점/10점 {'✅ APPROVED' if result.overall_satisfied else '❌ REJECTED'}")
        print(f"  💰 Cost: ${result.judge_cost:.4f}")
        print(f"  ⏱️ Time: {result.judge_time:.2f}s")

        # 카테고리별 상세 이유 출력
        print(f"\n📋 상세 평가 이유:")
        print(f"  📝 Syntax ({result.syntax_score}점): {result.syntax_reason[:200]}{'...' if len(result.syntax_reason) > 200 else ''}")
        print(f"  🛡️ Security ({result.security_score}점): {result.security_reason[:200]}{'...' if len(result.security_reason) > 200 else ''}")
        print(f"  🔒 Safety ({result.safety_score}점): {result.safety_reason[:200]}{'...' if len(result.safety_reason) > 200 else ''}")
        print(f"  ⚡ Optimization ({result.optimization_score}점): {result.optimization_reason[:200]}{'...' if len(result.optimization_reason) > 200 else ''}")

        if result.detailed_feedback:
            print(f"\n📋 전체 상세 피드백:")
            print(result.detailed_feedback)

        print("\n" + "=" * 80)
        print("✅ 평가 완료!")

    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()

def print_usage():
    """사용법 출력"""
    print("사용법: python test_agent_as_judge.py <history_id>")
    print("예시: python test_agent_as_judge.py 83")
    print("")
    print("설명:")
    print("  history_id: 데이터베이스의 history 테이블에서 평가할 레코드의 ID")

if __name__ == "__main__":

    # Agent-as-a-Judge 설정 (Ollama 사용 - 더 가벼운 모델)
    os.environ["DEFAULT_LLM"] = "ollama/llama3.2:1b"  # 가장 빠른 모델
    os.environ["OPENAI_API_KEY"] = "not-needed-for-ollama"
    os.environ["LITELLM_REQUEST_TIMEOUT"] = "600"
    os.environ["OLLAMA_REQUEST_TIMEOUT"] = "600"
    os.environ["LITELLM_DROP_PARAMS"] = "true"
    os.environ["LITELLM_LOG"] = "ERROR"

    # 타임아웃 설정 확인
    print("✅ 환경변수 타임아웃 설정: 600초")

    # .env 파일에서 데이터베이스 정보 확인
    required_env_vars = ["user", "password", "host", "port", "dbname"]
    missing_vars = []

    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ .env 파일에 다음 환경변수가 누락되었습니다: {', '.join(missing_vars)}")
        print("📋 .env 파일 예시:")
        print("user=postgres.zjlfoqnspubgwpeabaeo")
        print("password=JQyu0PKHgwA478Vs")
        print("host=aws-1-ap-northeast-2.pooler.supabase.com")
        print("port=5432")
        print("dbname=postgres")
        sys.exit(1)

    print(f"✅ .env 파일에서 환경변수 로드 완료")
    print(f"📊 데이터베이스: {os.getenv('host')}:{os.getenv('port')}/{os.getenv('dbname')}")

    # 명령행 인수 확인
    if len(sys.argv) != 2:
        print("❌ 잘못된 사용법입니다.")
        print_usage()
        sys.exit(1)

    try:
        history_id = int(sys.argv[1])
        test_security_judge(history_id)
    except ValueError:
        print("❌ history_id는 정수여야 합니다.")
        print_usage()
        sys.exit(1)
