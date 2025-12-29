## Environment
- Supported only on 64-bit Linux (Ubuntu 18.04, 20.04).
- For detailed system requirements, see the [documentation](https://docs.stackstorm.com/install/system_requirements.html).
- Automation is implemented using the open-source project [StackStorm](https://github.com/StackStorm/st2?tab=readme-ov-file).

## Setup
- Install StackStorm with:
  `curl -sSL https://stackstorm.com/packages/install.sh | bash -s -- --user=st2admin --password=Ch@ngeMe`
- After installation, verify the web UI is accessible via localhost or your server IP. The default port is 80.
- Run the `reinstall.sh` script to install the [pack](https://docs.stackstorm.com/packs.html).
  - If you encounter errors during execution, delete the Git directory with `rm -rf .git` and try again.


## Test
- After finishing setup, to verify everything is working, send a POST request with the payload below to http://{YOUR_IP}/api/v1/webhooks/ids.
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
