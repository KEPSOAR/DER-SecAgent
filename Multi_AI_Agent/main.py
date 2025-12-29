import sys
from kepsoar.graph.build_graph import build
from kepsoar.graph.states import operation_mode
from kepsoar.db.db_connect import fetch_log_storage, fetch_history_storage_by_key
from kepsoar.utils.parser import parse, parse_from_history
from kepsoar.graph.states import operation_mode, script_engineering_type

# parm
def main(key: int, mode: operation_mode, eng: script_engineering_type):

    if mode == operation_mode.SCRIPT_GEN:
        log = fetch_log_storage(key)
        input = parse(log)
        input["is_script_changed"] = False
        input["script_engineering"] = eng or script_engineering_type.ZERO_SHOT
    else:
        log = fetch_history_storage_by_key(key)
        input = parse_from_history(log)
        input["is_script_changed"] = False
        input["script_engineering"] = eng or script_engineering_type.ZERO_SHOT

    input["mode"] = mode
    soar = build()

    print(f"== {mode.name} | script_engineering={input['script_engineering'].value} ==")
    for out in soar.stream(input):
        print(out)
    print("―" * 120)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 main.py <key> <script|report> [zero|few|cot|tot]")
        sys.exit(1)

    try:
        key_param = int(sys.argv[1])
        mode_str = sys.argv[2].lower()
        mode_enum = operation_mode(mode_str)
        eng_enum = None
        if len(sys.argv) >= 4:
            eng_enum = script_engineering_type(sys.argv[3].lower())
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


    main(key_param, mode_enum, eng_enum)
