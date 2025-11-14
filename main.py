import argparse
import json
from calculate_solution import compute_move_transition, compute_full_sequence
from utils import is_valid_rods_state, print_solution, save_solution


def input_method_all_together():
    '''
    Input method where all rings start on one rod and must move to target rod.
    Output:
        - rods: a dictionary, in the form {1: <list>, 2: <list>, 3: <list>}
            - 1: the state of the first (left) rod, represented as a list of rings ordered from bottom to top
            - 2: the state of the second (middle) rod, represented as a list of rings ordered from bottom to top
            - 3: the state of the third (right) rod, represented as a list of rings ordered from bottom to top
        - target: the number of the target rod
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
        print(f"❌ Problem has an invalid configuration!")
        return None, None
    return rods, target

def input_method_custom():
    '''
    Input method where user specifies rings for each rod individually.
    Output:
        - rods: a dictionary, in the form {1: <list>, 2: <list>, 3: <list>}
            - 1: the state of the first (left) rod, represented as a list of rings ordered from bottom to top
            - 2: the state of the second (middle) rod, represented as a list of rings ordered from bottom to top
            - 3: the state of the third (right) rod, represented as a list of rings ordered from bottom to top
        - target: the number of the target rod
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
        print(f"❌ Problem has an invalid configuration!")
        return None, None
    return rods, target

def input_method_problems():
    '''
    Input method where user selects from predefined problems.
    Output:
        - rods: a dictionary, in the form {1: <list>, 2: <list>, 3: <list>}
            - 1: the state of the first (left) rod, represented as a list of rings ordered from bottom to top
            - 2: the state of the second (middle) rod, represented as a list of rings ordered from bottom to top
            - 3: the state of the third (right) rod, represented as a list of rings ordered from bottom to top
        - target: the number of the target rod
    '''
    try:
        with open("problems.json", "r") as f:
            problems_data = json.load(f)
    except FileNotFoundError:
        print("❌ problems.json file not found!")
        return None, None
    except json.JSONDecodeError:
        print("❌ Invalid JSON format in problems.json!")
        return None, None
    problems = problems_data['problems']
    print("\nAvailable Hanoi Tower Problems:")
    for num, problem in problems.items():
        print(f"{num}. {problem['description']}")
        print(f"   Initial: rod 1 = {problem['initial_state']['1']}, rod 2 = {problem['initial_state']['2']}, rod 3 = {problem['initial_state']['3']}")
        print(f"   Target: Rod {problem['target']}")
        print()
    while True:
        try:
            choice = input("Enter the problem number you want to solve: ").strip()
            if choice not in problems:
                print(f"❌ Problem {choice} does not exist. Please choose from {', '.join(problems.keys())}.")
                continue
            selected_problem = problems[choice]
            rods_state = {
                1: selected_problem['initial_state']['1'],
                2: selected_problem['initial_state']['2'],
                3: selected_problem['initial_state']['3']
            }
            target = selected_problem['target']
            if not is_valid_rods_state(rods_state):
                print(f"❌ Problem {choice} has an invalid configuration!")
                continue
            print(f"\n✅ Selected Problem {choice}: {selected_problem['description']}")
            return rods_state, target
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tower of Hanoi Solver")
    parser.add_argument("--input-method", choices = ["classic", "manual", "preset"], 
                       help = "Choose input method: 'classic' (all-together, default), 'manual' (custom), or 'preset' (problems)")
    args = parser.parse_args()
    input_method = args.input_method or "classic"
    while True:
        try:
            rods = None
            target = None
            if input_method == "classic":
                rods, target = input_method_all_together()
            elif input_method == "manual":
                rods, target = input_method_custom()
            elif input_method == "preset":                
                rods, target = input_method_problems()
            if rods is None:
                continue
            seq = compute_full_sequence(rods, target)
            print_solution(seq)
            while True:
                try:
                    save_choice = input("\nDo you want to save this solution? (y/n, default=n): ").strip().lower()
                    if save_choice in ["", "n"]:
                        break
                    elif save_choice == "y":
                        save_solution(rods, seq)
                        break
                    else:
                        print("Please enter 'y' or 'n'!")
                except Exception as e:
                    print(f"Error during save prompt: {e}")
                    break
        except KeyboardInterrupt:
            print("\nProgram terminated by user.")
            break
