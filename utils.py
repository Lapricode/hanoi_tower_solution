import json
from datetime import datetime


def is_valid_rods_state(rods):
    '''
    Input:
        - rods: a dictionary, in the form {1: <list>, 2: <list>, 3: <list>}
            - 1: the state of the first (left) rod, represented as a list of rings ordered from bottom to top
            - 2: the state of the second (middle) rod, represented as a list of rings ordered from bottom to top
            - 3: the state of the third (right) rod, represented as a list of rings ordered from bottom to top
    Output:
        - a boolean indicating if the rods state given is valid
    '''
    r1, r2, r3 = rods[1], rods[2], rods[3]
    r = r1 + r2 + r3
    rods_list = [("1", r1), ("2", r2), ("3", r3)]
    total_rings = sum(len(rk) for name, rk in rods_list)
    invalid_rods_order = r1[::-1] != sorted(r1) or r2[::-1] != sorted(r2) or r3[::-1] != sorted(r3)
    invalid_rings_given = sorted(r) != list(range(1, len(r) + 1))
    if total_rings == 0:
        print("❌ At least one ring must be placed on a rod!")
        return False
    if invalid_rods_order:
        print(f"❌ The rings do not follow the rules in terms of order, in rods {', '.join([name for name, rk in rods_list if rk[::-1] != sorted(rk)])}!")
        return False
    if invalid_rings_given:
        print(f"❌ Some rings are missing or duplicates show up (the available rings are {', '.join(sorted([str(rk) for rk in r]))})!")
        return False
    return True

def print_solution(seq):
    '''
    Input:
        - seq: a dictionary, in the form {m1: [r1, x1, y1], m2: [r2, x2, y2], ...}
            - m: the number of the move
            - r: the number of the ring that moves during the transition of move m
            - x: the number of the rod from which the transition of move m starts
            - y: the number of the rod to which the transition of move m ends
    '''
    print()
    for m in range(1, len(seq) + 1):
        print(f"{m}:  {int(seq[m][1])} -> {int(seq[m][2])} ({int(seq[m][0])})")

def verify_solution(rods, seq, target):
    '''
    Input:
        - rods: a dictionary, in the form {1: <list>, 2: <list>, 3: <list>}
            - 1: the state of the first (left) rod, represented as a list of rings ordered from bottom to top
            - 2: the state of the second (middle) rod, represented as a list of rings ordered from bottom to top
            - 3: the state of the third (right) rod, represented as a list of rings ordered from bottom to top
        - seq: a dictionary, in the form {m1: [r1, x1, y1], m2: [r2, x2, y2], ...}
            - m: the number of the move
            - r: the number of the ring that moves during the transition of move m
            - x: the number of the rod from which the transition of move m starts
            - y: the number of the rod to which the transition of move m ends
        - target: the number of the target rod
    Output:
        - a boolean indicating whether the solution is valid
    '''
    current_rods = {rod: rings[:] for rod, rings in rods.items()}    
    for m in range(1, len(seq) + 1):
        ring, source, dest = seq[m]
        if not current_rods[source] or current_rods[source][-1] != ring:
            print(f"❌ Move {m}: Ring {ring} is not on top of rod {source}!")
            return False
        if current_rods[dest] and current_rods[dest][-1] < ring:
            print(f"❌ Move {m}: Cannot place ring {ring} on top of smaller ring {current_rods[dest][-1]} on rod {dest}!")
            return False
        current_rods[source].pop()
        current_rods[dest].append(ring)
    expected_final = list(range(sum(len(current_rods[rod]) for rod in [1, 2, 3]), 0, -1))
    if current_rods[target] == expected_final and all(len(current_rods[rod]) == 0 for rod in [1, 2, 3] if rod != target):
        print(f"✅ Solution is valid! All rings are correctly placed on the target rod {target}!")
        return True
    else:
        print("❌ Solution is invalid! Final state does not match expected configuration!")
        print(f"Expected: Rod {target} = {expected_final}, other rods empty.")
        print(f"Actual: Rod 1 = {current_rods[1]}, Rod 2 = {current_rods[2]}, Rod 3 = {current_rods[3]}.")
        return False

def _format_json_mixed(obj, indent = 2, level = 0):
    """
    Recursively format `obj` as JSON:
    - dicts are pretty-printed with newlines/indentation
    - lists are always dumped compactly (single-line) via json.dumps
    - primitives use json.dumps
    Returns a string of valid JSON.
    """
    pad = ' ' * (indent * level)
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        pieces = []
        for i, (k, v) in enumerate(obj.items()):
            key = json.dumps(k)
            value_str = _format_json_mixed(v, indent = indent, level = level + 1)
            pieces.append(f'{" " * (indent * (level+1))}{key}: {value_str}')
        return "{\n" + ",\n".join(pieces) + "\n" + pad + "}"
    elif isinstance(obj, list):
        return json.dumps(obj)
    else:
        return json.dumps(obj)

def save_solution(rods, target, seq, file = "solutions.json"):
    """
    Save solution to JSON file with numbered indications like problems.json
    Input:
        - rods: a dictionary, in the form {1: <list>, 2: <list>, 3: <list>}
            - 1: the state of the first (left) rod, represented as a list of rings ordered from bottom to top
            - 2: the state of the second (middle) rod, represented as a list of rings ordered from bottom to top
            - 3: the state of the third (right) rod, represented as a list of rings ordered from bottom to top
        - target: the number of the target rod
        - seq: a dictionary, in the form {m1: [r1, x1, y1], m2: [r2, x2, y2], ...}
            - m: the number of the move
            - r: the number of the ring that moves during the transition of move m
            - x: the number of the rod from which the transition of move m starts
            - y: the number of the rod to which the transition of move m ends
        - file: the JSON file's name to save the solution to
    Output:
        - a boolean indicating whether the solution has been saved successfully
    """
    try:
        try:
            with open(file, "r") as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {"solutions": {}}
        if "solutions" not in existing_data:
            existing_data["solutions"] = {}
        solution_numbers = [int(num) for num in existing_data["solutions"].keys() if str(num).isdigit()]
        next_number = max(solution_numbers) + 1 if solution_numbers else 1
        solution_data = {
            "timestamp": datetime.now().isoformat(),
            "initial_state": {
                "1": rods[1],
                "2": rods[2],
                "3": rods[3]
            },
            "target": target,
            "total_moves": len(seq),
            "moves_sequence": {str(k): v for k, v in seq.items()}
        }
        existing_data["solutions"][str(next_number)] = solution_data
        json_str = _format_json_mixed(existing_data, indent = 2)
        with open(file, "w") as f:
            f.write(json_str)
        print(f"✅ Solution saved as #{next_number} to {file}!")
        return True
    except Exception as e:
        print(f"❌ Failed to save solution: {e}!")
        return False

def load_solution(file = "solutions.json", sol_num = 1):
    """
    Load a specific solution from JSON file
    Input:
        - file: the JSON file's name to load the solution from
        - sol_num: the number of the solution to load
    Output:
        - initial_state: a dictionary, in the form {1: <list>, 2: <list>, 3: <list>}
            - 1: the initial state of the first (left) rod, represented as a list of rings ordered from bottom to top
            - 2: the initial state of the second (middle) rod, represented as a list of rings ordered from bottom to top
            - 3: the initial state of the third (right) rod, represented as a list of rings ordered from bottom to top
        - target: the number of the target rod
        - seq: a dictionary, in the form {m1: [r1, x1, y1], m2: [r2, x2, y2], ...}
            - m: the number of the move
            - r: the number of the ring that moves during the transition of move m
            - x: the number of the rod from which the transition of move m starts
            - y: the number of the rod to which the transition of move m ends
    """
    try:
        with open(file, "r") as f:
            data = json.load(f)
        if "solutions" not in data:
            print(f"❌ No solutions found in {file}!")
            return None, None, None
        solutions = data["solutions"]
        if str(sol_num) not in solutions:
            available_solutions = [num for num in solutions.keys() if num.isdigit()]
            print(f"❌ Solution #{sol_num} not found!")
            print(f"Available solutions: {', '.join(sorted(available_solutions))}")
            return None, None, None
        solution = solutions[str(sol_num)]
        initial_state = {
            1: solution["initial_state"]["1"],
            2: solution["initial_state"]["2"], 
            3: solution["initial_state"]["3"]
        }
        target = solution["target"]
        seq = solution["moves_sequence"]
        print(f"✅ Loaded solution #{sol_num} from {file}")
        print(f"Timestamp: {solution.get('timestamp', 'Unknown')}")
        print(f"Total moves: {solution.get('total_moves', len(seq))}")
        return initial_state, target, seq
    except FileNotFoundError:
        print(f"❌ File {file} not found!")
        return None, None, None
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON format in {file}!")
        return None, None, None
    except KeyError as e:
        print(f"❌ Missing expected key in solution data: {e}!")
        return None, None, None
    except Exception as e:
        print(f"❌ Failed to load solution: {e}!")
        return None, None, None

def simplify_sequence(seq):
    '''
    Simplify the moves sequence, reducing the number of moves and keeping the solution valid.
        - test 1: check for consecutive moves done with the same ring, and substitute them with the corresponding single effective move
        - test 2: check if moves in the form {m: [r, z, z]} (same start and final rods) are left in the sequence
    Input:
        - seq: a dictionary, in the form {m1: [r1, x1, y1], m2: [r2, x2, y2], ...}
            - m: the number of the move
            - r: the number of the ring that moves during the transition of move m
            - x: the number of the rod from which the transition of move m starts
            - y: the number of the rod to which the transition of move m ends
    Output:
        - simple_seq: the simplified sequence, in the same form as the seq
    '''
    if not seq:
        return {}
    moves = []
    for move_num in sorted(seq.keys()):
        ring, source, dest = seq[move_num]
        moves.append((ring, source, dest))
    changed = True
    while changed:
        changed = False
        k = 0
        while k < len(moves) - 1:
            current_move = moves[k]
            next_move = moves[k + 1]
            if current_move[0] == next_move[0]:
                moves[k] = (current_move[0], current_move[1], next_move[2])
                del moves[k+1]
                changed = True
                current_move = moves[k]
                if current_move[1] == current_move[2]:
                    del moves[k]
            else:
                k += 1
    simple_seq = {}
    for m, (ring, source, dest) in enumerate(moves):
        simple_seq[m + 1] = [ring, source, dest]    
    return simple_seq
