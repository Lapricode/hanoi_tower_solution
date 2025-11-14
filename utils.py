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
    invalid_rods_order = r1[::-1] != sorted(r1) and r2[::-1] != sorted(r2) and r3[::-1] != sorted(r3)
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
        print("✅ Solution is valid! All rings are correctly placed on the target rod!")
        return True
    else:
        print("❌ Solution is invalid! Final state does not match expected configuration!")
        print(f"Expected: Rod {target} = {expected_final}, other rods empty.")
        print(f"Actual: Rod 1 = {current_rods[1]}, Rod 2 = {current_rods[2]}, Rod 3 = {current_rods[3]}.")
        return False

def save_solution(rods, seq):
    """
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
    Output:
        - a boolean indicating whether the solution has been saved successfully
    """
    try:
        solution_data = {
            "timestamp": datetime.now().isoformat(),
            "initial_rods": [rods[r] for r in [1, 2, 3]],
            "total_moves": len(seq),
            "moves_sequence": seq
        }
        try:
            with open("solution.json", "r") as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {"solutions": []}
        existing_data["solutions"].append(solution_data)
        with open("solution.json", "w") as f:
            json.dump(existing_data, f, indent = 2)
        print(f"✅ Solution saved successfully to solution.json!")
        return True
    except Exception as e:
        print(f"❌ Failed to save solution: {e}!")
        return False
    
def simplify_sequence(seq):
    '''
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
        i = 0
        while i < len(moves) - 1:
            current_move = moves[i]
            next_move = moves[i + 1]
            if (current_move[0] == next_move[0] and
                current_move[1] == next_move[2] and
                current_move[2] == next_move[1]):
                del moves[i:i+2]
                changed = True
            else:
                i += 1
    simple_seq = {}
    for m, (ring, source, dest) in enumerate(moves):
        simple_seq[m + 1] = [ring, source, dest]    
    return simple_seq
