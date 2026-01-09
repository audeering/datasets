"""Convert JSON files in build/json to the specification format.

This script transforms the Berkeley Function Calling Leaderboard JSON files
to match the data format specification for Audio Language Models.

Transformations:
- Convert role "user" to "human"
- Convert "content" key to "text"
- Wrap function definitions in Qwen format with "tools" in system message
- Convert parameter "type": "dict" to "type": "object" for JSON Schema compliance
- Flatten multi-turn question arrays into a conversation list
- For multi-turn benchmarks, fetch tool definitions from multi-turn-func-doc
"""

import json
from pathlib import Path


# Mapping from involved_classes names to func-doc files
CLASS_TO_FUNC_DOC = {
    "GorillaFileSystem": "gorilla-file-system.jsonl",
    "MathAPI": "math-api.jsonl",
    "MessageAPI": "message-api.jsonl",
    "TwitterAPI": "posting-api.jsonl",
    "TicketAPI": "ticket-api.jsonl",
    "TradingBot": "trading-bot.jsonl",
    "TravelAPI": "travel-booking.jsonl",
    "VehicleControlAPI": "vehicle-control.jsonl",
}


def load_func_docs(func_doc_dir):
    """Load all function documentation from jsonl files.

    Returns a tuple of:
    - func_docs: dict mapping class names to lists of function definitions
    - func_param_names: dict mapping function names to list of parameter names (in order)
    """
    func_docs = {}
    func_param_names = {}

    for class_name, filename in CLASS_TO_FUNC_DOC.items():
        filepath = func_doc_dir / filename
        if filepath.exists():
            functions = []
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        func = json.loads(line)
                        functions.append(func)

                        # Extract parameter names in order for positional arg mapping
                        params = func.get("parameters", {})
                        properties = params.get("properties", {})
                        required = params.get("required", [])

                        # Use required params first, then optional ones
                        param_names = list(required)
                        for prop_name in properties:
                            if prop_name not in param_names:
                                param_names.append(prop_name)

                        func_param_names[func["name"]] = param_names

            func_docs[class_name] = functions

    return func_docs, func_param_names


def convert_dict_to_object(obj):
    """Recursively convert type: "dict" to type: "object" in parameters."""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if key == "type" and value == "dict":
                result[key] = "object"
            else:
                result[key] = convert_dict_to_object(value)
        return result
    elif isinstance(obj, list):
        return [convert_dict_to_object(item) for item in obj]
    else:
        return obj


def convert_function_to_tool(func):
    """Convert a function definition to Qwen tool format."""
    return {
        "type": "function",
        "function": {
            "name": func["name"],
            "description": func.get("description", ""),
            "parameters": convert_dict_to_object(func.get("parameters", {})),
        },
    }


def convert_message(msg):
    """Convert a single message from old format to new format."""
    result = {}

    # Convert role
    role = msg.get("role", "")
    if role == "user":
        result["role"] = "human"
    elif role == "assistant":
        result["role"] = "assistant"
    elif role == "system":
        result["role"] = "system"
    else:
        result["role"] = role

    # Convert content to text
    if "content" in msg:
        result["text"] = msg["content"]

    # Copy other fields that might exist
    for key in msg:
        if key not in ("role", "content"):
            result[key] = msg[key]

    return result


def parse_function_call_string(call_str, func_param_names=None):
    """Parse a function call string like "cd(folder='document')" into name and arguments.

    Args:
        call_str: The function call string to parse
        func_param_names: Optional dict mapping function names to list of parameter names
                          (in order) for resolving positional arguments

    Returns (name, arguments_json_string) tuple.
    """
    # Find the function name (everything before the first '(')
    paren_idx = call_str.find("(")
    if paren_idx == -1:
        return call_str, "{}"

    name = call_str[:paren_idx]
    args_str = call_str[paren_idx + 1 : -1]  # Remove '(' and ')'

    if not args_str.strip():
        return name, "{}"

    # Parse the arguments - they're in Python syntax like: folder='document', x=123
    # Also handle positional arguments like: sort('file.txt')
    args = {}
    positional_args = []

    # Simple parsing: split by comma, handle '=' for keyword args
    current_key = None
    current_value = ""
    in_string = False
    string_char = None
    paren_depth = 0
    bracket_depth = 0
    has_equals = False  # Track if current arg has '='

    i = 0
    while i < len(args_str):
        char = args_str[i]

        if not in_string:
            if char in "\"'":
                in_string = True
                string_char = char
                current_value += char
            elif char == "(":
                paren_depth += 1
                current_value += char
            elif char == ")":
                paren_depth -= 1
                current_value += char
            elif char == "[":
                bracket_depth += 1
                current_value += char
            elif char == "]":
                bracket_depth -= 1
                current_value += char
            elif char == "=" and current_key is None and paren_depth == 0 and bracket_depth == 0:
                current_key = current_value.strip()
                current_value = ""
                has_equals = True
            elif char == "," and paren_depth == 0 and bracket_depth == 0:
                if has_equals and current_key is not None:
                    # Keyword argument
                    args[current_key] = parse_python_value(current_value.strip())
                elif current_value.strip():
                    # Positional argument
                    positional_args.append(parse_python_value(current_value.strip()))
                current_key = None
                current_value = ""
                has_equals = False
            else:
                current_value += char
        else:
            current_value += char
            if char == string_char and (i == 0 or args_str[i - 1] != "\\"):
                in_string = False
                string_char = None

        i += 1

    # Don't forget the last argument
    if has_equals and current_key is not None:
        args[current_key] = parse_python_value(current_value.strip())
    elif current_value.strip():
        positional_args.append(parse_python_value(current_value.strip()))

    # Map positional arguments to parameter names if we have the function definition
    if positional_args and func_param_names and name in func_param_names:
        param_names = func_param_names[name]
        for i, value in enumerate(positional_args):
            if i < len(param_names):
                args[param_names[i]] = value

    return name, json.dumps(args)


def parse_python_value(value_str):
    """Parse a Python value string into a Python value."""
    value_str = value_str.strip()

    # String values (single or double quoted)
    if (value_str.startswith("'") and value_str.endswith("'")) or \
       (value_str.startswith('"') and value_str.endswith('"')):
        return value_str[1:-1]

    # Boolean values
    if value_str == "True":
        return True
    if value_str == "False":
        return False

    # None
    if value_str == "None":
        return None

    # Try to parse as number
    try:
        if "." in value_str:
            return float(value_str)
        return int(value_str)
    except ValueError:
        pass

    # Return as-is (might be a complex expression)
    return value_str


def convert_ground_truth_simple(ground_truth):
    """Convert simple/parallel ground_truth format to tool-call list.

    Input format: [{"func_name": {"arg1": [val1], "arg2": [val2, alt_val2]}}]
    Output format: [{"name": "func_name", "arguments": "{...}"}]
    """
    tool_calls = []
    for item in ground_truth:
        if isinstance(item, dict):
            for func_name, args in item.items():
                # Take the first value from each argument's list of alternatives
                parsed_args = {}
                for arg_name, values in args.items():
                    if isinstance(values, list) and len(values) > 0:
                        parsed_args[arg_name] = values[0]
                    else:
                        parsed_args[arg_name] = values

                tool_calls.append({
                    "name": func_name,
                    "arguments": json.dumps(parsed_args),
                })
    return tool_calls


def convert_ground_truth_multi_turn(ground_truth_turn, func_param_names=None):
    """Convert multi-turn ground_truth format for a single turn to tool-call list.

    Input format: ["cd(folder='document')", "mkdir(dir_name='temp')"]
    Output format: [{"name": "cd", "arguments": "{...}"}, ...]

    Args:
        ground_truth_turn: List of function call strings
        func_param_names: Optional dict mapping function names to list of parameter names
    """
    tool_calls = []
    for call_str in ground_truth_turn:
        if isinstance(call_str, str):
            name, args_json = parse_function_call_string(call_str, func_param_names)
            tool_calls.append({
                "name": name,
                "arguments": args_json,
            })
    return tool_calls


def convert_file(data, func_docs=None, func_param_names=None):
    """Convert a single JSON file's data to the new format.

    Args:
        data: The original JSON data as a dict
        func_docs: Optional dict mapping class names to function definitions
                   (for multi-turn files)
        func_param_names: Optional dict mapping function names to list of parameter names
                          (for resolving positional arguments in multi-turn ground_truth)

    Returns a list representing the conversation.
    """
    # Skip if already converted (is a list)
    if isinstance(data, list):
        return data

    conversation = []

    # Handle function definitions - create system message with tools
    functions = data.get("function", [])
    tools = []
    all_tools_by_name = {}  # Map function name to tool definition

    if functions:
        # Handle case where function is an empty string (chatable format)
        if isinstance(functions, str) and functions == "":
            functions = []
        elif isinstance(functions, list) and len(functions) > 0:
            for func in functions:
                tool = convert_function_to_tool(func)
                tools.append(tool)
                all_tools_by_name[func["name"]] = tool

    # For multi-turn files, get tools from path field
    # path contains entries like "GorillaFileSystem.find", "TwitterAPI.post_tweet"
    path = data.get("path", [])
    if path and func_docs:
        # Build a set of required function names from path
        required_funcs = set()
        for entry in path:
            if "." in entry:
                class_name, func_name = entry.split(".", 1)
                required_funcs.add((class_name, func_name))

        # Find matching functions from func_docs
        for class_name, func_name in required_funcs:
            if class_name in func_docs:
                for func in func_docs[class_name]:
                    if func["name"] == func_name:
                        tool = convert_function_to_tool(func)
                        tools.append(tool)
                        all_tools_by_name[func_name] = tool
                        break

    # Handle missed_function - functions to be provided at later turns
    # Format: {"turn_idx": ["func_name1", "func_name2"], ...}
    missed_function = data.get("missed_function", {})
    missed_func_names = set()
    delayed_tools = {}  # Map turn_idx (int) to list of tool definitions

    for turn_idx_str, func_names in missed_function.items():
        turn_idx = int(turn_idx_str)
        delayed_tools[turn_idx] = []
        for func_name in func_names:
            missed_func_names.add(func_name)
            if func_name in all_tools_by_name:
                delayed_tools[turn_idx].append(all_tools_by_name[func_name])

    # Remove missed functions from initial tools list
    if missed_func_names:
        tools = [t for t in tools if t["function"]["name"] not in missed_func_names]

    # Build system message
    system_message = {"role": "system"}

    # Add initial_config if present (for multi-turn files)
    initial_config = data.get("initial_config")
    if initial_config:
        system_message["initial_config"] = initial_config

    # Add tools if we have any
    if tools:
        system_message["tools"] = tools

    # Only add system message if it has content beyond just role
    if len(system_message) > 1:
        conversation.append(system_message)

    # Handle questions - can be nested array (multi-turn) or string (chatable)
    questions = data.get("question", [])
    ground_truth = data.get("ground_truth", [])

    # Determine ground_truth format:
    # 1. Multi-turn: list of lists of strings [["func1()", "func2()"], ["func3()"]]
    # 2. String format (exec-*): list of strings ["func(args)"]
    # 3. Dict format (simple/parallel): list of dicts [{"func_name": {"arg": [val]}}]
    gt_format = None
    if ground_truth and isinstance(ground_truth, list) and len(ground_truth) > 0:
        first_item = ground_truth[0]
        if isinstance(first_item, list):
            gt_format = "multi_turn"
        elif isinstance(first_item, str):
            gt_format = "string"
        elif isinstance(first_item, dict):
            gt_format = "dict"

    if isinstance(questions, str):
        # Chatable format: question is a plain string
        conversation.append({"role": "human", "text": questions})
    elif isinstance(questions, list):
        # Standard format: nested array of turns
        for turn_idx, turn in enumerate(questions):
            # Add user message(s) for this turn
            if isinstance(turn, list):
                # Each turn is a list of messages
                for msg in turn:
                    if isinstance(msg, dict):
                        converted = convert_message(msg)
                        conversation.append(converted)
            elif isinstance(turn, dict):
                # Single message format
                converted = convert_message(turn)
                conversation.append(converted)

            # Add delayed tools if any are scheduled for this turn
            # (must come before assistant response so the assistant can use them)
            if turn_idx in delayed_tools and delayed_tools[turn_idx]:
                delayed_system_msg = {
                    "role": "system",
                    "tools": delayed_tools[turn_idx]
                }
                conversation.append(delayed_system_msg)

            # Add assistant response if we have ground_truth for this turn
            if gt_format == "multi_turn":
                # Multi-turn format: ground_truth[turn_idx] is a list of function call strings
                if turn_idx < len(ground_truth):
                    gt_turn = ground_truth[turn_idx]
                    if gt_turn:  # Skip empty turns
                        tool_calls = convert_ground_truth_multi_turn(gt_turn, func_param_names)
                        if tool_calls:
                            assistant_msg = {"role": "assistant", "tool-call": tool_calls}
                            conversation.append(assistant_msg)
            elif turn_idx == 0 and gt_format == "string":
                # String format (exec-*): list of function call strings for single turn
                tool_calls = convert_ground_truth_multi_turn(ground_truth, func_param_names)
                if tool_calls:
                    assistant_msg = {"role": "assistant", "tool-call": tool_calls}
                    conversation.append(assistant_msg)
            elif turn_idx == 0 and gt_format == "dict":
                # Dict format (simple/parallel): all ground_truth items are for the single turn
                tool_calls = convert_ground_truth_simple(ground_truth)
                if tool_calls:
                    assistant_msg = {"role": "assistant", "tool-call": tool_calls}
                    conversation.append(assistant_msg)

    return conversation


def convert_json_file(input_path, output_path, func_docs=None, func_param_names=None):
    """Convert a single JSON file from old format to new format."""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert to conversation format
    conversation = convert_file(data, func_docs, func_param_names)

    # Write the converted data
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(conversation, f, ensure_ascii=False, indent=2)


def is_multi_turn_dir(dir_name):
    """Check if a directory is a multi-turn benchmark directory."""
    return "multi-turn" in dir_name


def main():
    """Convert all JSON files in build/json directory."""
    base_dir = Path(__file__).parent / "build"
    json_dir = base_dir / "json"
    func_doc_dir = base_dir / "multi-turn-func-doc"

    if not json_dir.exists():
        print(f"Directory not found: {json_dir}")
        return

    # Load function documentation for multi-turn files
    func_docs = {}
    func_param_names = {}
    if func_doc_dir.exists():
        print(f"Loading function documentation from {func_doc_dir}")
        func_docs, func_param_names = load_func_docs(func_doc_dir)
        print(f"Loaded {len(func_docs)} class definitions, {len(func_param_names)} function parameter mappings")

    # Find all JSON files
    json_files = list(json_dir.rglob("*.json"))
    total = len(json_files)

    print(f"Found {total} JSON files to convert")

    converted = 0
    skipped = 0
    errors = []

    for json_file in json_files:
        try:
            # Determine if this is a multi-turn file
            parent_dir = json_file.parent.name
            is_multi_turn = is_multi_turn_dir(parent_dir)
            use_func_docs = func_docs if is_multi_turn else None
            use_param_names = func_param_names if is_multi_turn else None

            convert_json_file(json_file, json_file, use_func_docs, use_param_names)
            converted += 1
            if converted % 500 == 0:
                print(f"Converted {converted}/{total} files...")
        except Exception as e:
            errors.append((str(json_file), str(e)))

    print(f"\nConversion complete: {converted}/{total} files converted")
    if skipped:
        print(f"Skipped {skipped} already-converted files")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for path, error in errors[:10]:  # Show first 10 errors
            print(f"  {path}: {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")


if __name__ == "__main__":
    main()
