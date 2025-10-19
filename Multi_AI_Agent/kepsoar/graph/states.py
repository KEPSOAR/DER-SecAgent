from typing_extensions import TypedDict

from enum import Enum, unique
from datetime import datetime

# State declalation
# enums
@unique
class operation_mode(Enum):
    SCRIPT_GEN = "script"
    REPORT_GEN = "report"

@unique
class script_engineering_type(Enum):
    ZERO_SHOT = "zero"
    FEW_SHOT = "few"
    COT = "cot"
    TOT = "tot"

@unique
class attack_type(Enum):
    DoS = "DoS"
    Probe = "Probe"
    R2L = "R2L"
    U2R = "U2R"
    MITM = "MITM"
    BruteForce = "BruteForce"

@unique
class risk_level_type(Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"
    Extreme = "Extreme"

# langgraph state definition
class soar_input(TypedDict):
    id: int
    event_time: datetime
    device_ip: str
    device_name: str
    source_institution_code: str
    source_ip: str
    source_port: int
    source_asset_name: str
    source_country: str
    source_mac: str
    dest_institution_code: str
    dest_ip: str
    dest_port: int
    dest_asset_name: str
    dest_country: str
    dest_mac: str
    protocol: str
    attack_type: attack_type
    account: str
    chain_of_thought: str
    mode: operation_mode
    is_script_changed: bool #TODO use this
    script: str
    script_engineering: script_engineering_type

class caution_eval_state(TypedDict):
    id: int
    event_time: datetime
    device_ip: str
    device_name: str
    source_institution_code: str
    source_ip: str
    source_port: int
    source_asset_name: str
    source_mac: str
    source_country: str
    dest_institution_code: str
    dest_ip: str
    dest_port: int
    dest_asset_name: str
    dest_mac: str
    dest_country: str
    protocol: str
    attack_type: attack_type
    account: str
    script: str
    caution: bool

class report_state(TypedDict):
    id: int
    event_time: datetime
    device_ip: str
    device_name: str
    source_institution_code: str
    source_ip: str
    source_mac: str
    source_port: int
    source_asset_name: str
    source_country: str
    dest_institution_code: str
    dest_ip: str
    dest_mac: str
    dest_port: int
    dest_asset_name: str
    dest_country: str
    protocol: str
    attack_type: attack_type
    account: str
    script: str
    report: str

# need add message??
class soar_output(TypedDict):
    report: str
    script: str
