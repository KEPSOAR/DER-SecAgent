## Environment
- 64 bit linux 환경 (Ubuntu 18.04, 20.04 버전)에서만 동작 가능합니다.
- 자세한 시스템 요구사항은 [링크](https://docs.stackstorm.com/install/system_requirements.html)를 참고해주세요.
- 자동화의 경우 오픈소스 라이브러리인 [StackStorm](https://github.com/StackStorm/st2?tab=readme-ov-file)으로 구현되었습니다.

## Setup
- `curl -sSL https://stackstorm.com/packages/install.sh | bash -s -- --user=st2admin --password=Ch@ngeMe` 명령어를 통해 Stackstorm을 설치해야 합니다.
- 설치 후 localhost나 ip주소를 통해 웹페이지가 정상적으로 보이는지 확인해주세요. 기본 포트는 80번 포트를 사용하고 있습니다.
- `reinstall.sh` 파일을 실행시켜 [팩](https://docs.stackstorm.com/packs.html)을 설치합니다.
  - 실행 과정에서 오류가 뜰 경우 `rm -rf .git`으로 깃 디렉토리를 삭제 후에 다시 실행하면 됩니다.


## Test
- 모든 셋업 이후에 정상적으로 동작하는지 확인하려면 http://{YOUR_IP}/api/v1/webhooks/ids 주소에 아래 데이터를 POST 요청으로 보내면 됩니다.
```
{
        "event_time": "2025-01-01 00:00:00",
        "device_ip": "10.10.10.10",
        "device_name": "Main Firewall",
        "source_institution_code": "TEST_00",
        "source_ip": "123.123.123.123",
        "source_port": 123,
        "source_asset_name": "John Doe",
        "source_country": "South Korea",
				"source_mac": "00-1B-63-84-45-E6",
        "dest_institution_code": "TEST_99",
        "dest_ip": "100.0.0.100",
        "dest_port": 5678,
        "dest_asset_name": "Server A",
        "dest_country": "South Korea",
				"dest_mac": "00-1B-63-84-45-E6",
        "protocol": "udp",
        "action": "deny",
				"attack_type": "DoS",
				"account": "kkm1447@naver.com",
				"risk_level": "Low"
      }
```
