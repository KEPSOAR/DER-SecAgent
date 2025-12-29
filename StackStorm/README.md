## DER-SecAgent: StackStorm Automation Pack

> Automation (webhooks, actions, workflows) for DER-SecAgent using StackStorm.

---

## Key Features

- **Webhook-driven automation**: Receives IDS and agent events via webhooks defined in `rules/*.yaml` (e.g., `ids.yaml`, `agent_report_web_hook.yaml`, `agent_script_web_hook.yaml`, `slack_web_hook.yaml`).
- **Actions and workflows**: Reusable actions in `actions/*.py|.yaml` and workflows in `actions/workflows/*.yaml`.
- **ChatOps-ready**: Slack webhook rule available for ChatOps-style approvals/notifications.
- **One-command pack install**: Use `reinstall.sh` to (re)install the pack into StackStorm.

---

## Environment

- Supported only on 64-bit Linux (Ubuntu 18.04, 20.04).
- For detailed system requirements, see the [StackStorm system requirements](https://docs.stackstorm.com/install/system_requirements.html).
- Automation is implemented using the open-source project [StackStorm](https://github.com/StackStorm/st2?tab=readme-ov-file).

---

## Getting Started

### 1) Install StackStorm

```bash
curl -sSL https://stackstorm.com/packages/install.sh | bash -s -- --user=st2admin --password=Ch@ngeMe
```

### 2) Install the DER-SecAgent pack

```bash
./reinstall.sh
```

- If you encounter errors during execution, delete the Git directory and try again:

```bash
rm -rf .git
./reinstall.sh
```

### 3) Access the Web UI

- Verify the web UI is accessible via localhost or your server IP (default port: 80).

---

## Test (Webhook)

- After finishing setup, to verify everything is working, send a POST request to `http://{YOUR_IP}/api/v1/webhooks/ids` with the payload below.

```json
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
