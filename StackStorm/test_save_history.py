#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
save_history.py 테스트 스크립트
"""

import sys
import os
sys.path.append('/home/kyungmink/kepsoar/actions')

from save_history import SaveHistory

def test_save_history():
    """save_history 액션 테스트"""
    
    # 터미널 선택 부분의 데이터 사용
    agent_script = """iptables -A INPUT -s 39.119.222.178 -p tcp --dport 80 -j DROP

iptables -A INPUT -p tcp --dport 80 -m limit --limit 100/minute -j ACCEPT

iptables -I INPUT 1 -s 39.119.222.178 -j DROP"""
    
    user_script = """iptables -A INPUT -s 39.119.222.178 -p tcp --dport 80 -j DROP

iptables -A INPUT -p tcp --dport 80 -m limit --limit 100/minute -j ACCEPT"""
    
    changed_reason = ""
    log_id = "1"
    caution = "True"
    
    print("save_history 액션 테스트 시작...")
    print(f"log_id: {log_id}")
    print(f"caution: {caution}")
    print(f"changed_reason: '{changed_reason}'")
    print("\nagent_script:")
    print(agent_script)
    print("\nuser_script:")
    print(user_script)
    print("\n" + "="*50)
    
    # SaveHistory 액션 실행
    action = SaveHistory()
    
    try:
        result = action.run(
            agent_script=agent_script,
            user_script=user_script,
            changed_reason=changed_reason,
            log_id=log_id,
            caution=caution
        )
        print(f"\n액션 실행 결과: {result}")
        
    except Exception as e:
        print(f"\n에러 발생: {e}")

if __name__ == "__main__":
    test_save_history()
