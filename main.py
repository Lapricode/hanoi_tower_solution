import argparse
from calculate_solution import compute_move_transition, compute_full_sequence
from utils import is_valid_rods_state, print_solution, save_solution


def input_method_all_together():
    '''
    Input method where all rings start on one rod and must move to target rod.
    '''
    while True:
        try:
            n = int(input("\nGive the number of rings (type an integer greater than 1): "))
            if n < 1:
                print("❌ The number of rings must be greater than 1!")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid integer.")
    while True:
        try:
            start = int(input("Give the starting rod (type 1, 2 or 3): "))
            if start not in (1, 2, 3):
                print("❌ The starting rod must be 1, 2, or 3!")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid integer.")
    while True:
        try:
            target = int(input("Give the target rod (type 1, 2 or 3): "))
            if target not in (1, 2, 3):
                print("❌ The target rod must be 1, 2, or 3!")
                continue
            if start == target:
                print("❌ The starting and target rods must be different!")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid integer.")
    rods = {1: [], 2: [], 3: []}
    rods[start] = list(range(n, 0, -1))
    if not is_valid_rods_state(rods):
        return None, None
    return rods, target

def input_method_custom():
    '''
    Input method where user specifies rings for each rod individually.
    '''
    rods = {1: [], 2: [], 3: []}
    print("\nEnter rings for each rod (bottom to top, comma-separated).")
    print("Example: '3, 2, 1' means ring 3 at bottom, then 2, then 1 at top.")
    print("Leave empty to have no rings on that rod.")
    for rod in [1, 2, 3]:
        while True:
            try:
                input_str = input(f"Rings for rod {rod} (bottom to top, comma-separated): ").strip()
                if not input_str:
                    rods[rod] = []
                    break
                rings = [int(x.strip()) for x in input_str.split(',')]
                rods[rod] = rings
                break
            except ValueError:
                print("❌ Please enter valid integers separated by commas!")
    while True:
        try:
            target = int(input("Give the target rod (type 1, 2 or 3): "))
            if target not in (1, 2, 3):
                print("❌ The target rod must be 1, 2, or 3!")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid integer!")
    if not is_valid_rods_state(rods):
        return None, None
    return rods, target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tower of Hanoi Solver")
    parser.add_argument("--input-method", choices = ["a", "c"], 
                       help = "Choose input method: 'a' (for all-together, default) or 'c' (for custom)")
    args = parser.parse_args()
    input_method = args.input_method or "a"
    while True:
        try:
            rods = None
            target = None
            if input_method == "a":
                rods, target = input_method_all_together()
            elif input_method == "c":
                rods, target = input_method_custom()
            if rods is None:
                continue
            seq = compute_full_sequence(rods, target)
            print_solution(seq)
        except KeyboardInterrupt:
            print("\nProgram terminated by user.")
            break
