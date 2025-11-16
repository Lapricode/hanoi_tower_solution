#!/usr/bin/env python3
import sys
import json
from calculate_solution import compute_full_sequence
from utils import save_solution


def solve_problems(problem_numbers):
    """
    Solve specified problems from problems.json and save solutions
    
    Args:
        problem_numbers: list of problem numbers to solve
    """
    if not problem_numbers:
        print("❌ No problem numbers provided!")
        print("Usage: python solve_problems.py 1 2 3 ...")
        return
    
    try:
        # Load problems
        with open("problems.json", "r") as f:
            data = json.load(f)
        
        if "problems" not in data:
            print("❌ No problems found in problems.json!")
            return
        
        problems = data["problems"]
        print(f"🔧 Solving {len(problem_numbers)} problem(s): {', '.join(problem_numbers)}")
        print("=" * 60)
        
        solved_count = 0
        failed_count = 0
        correct_solutions = []
        wrong_solutions = []
        
        for problem_num in problem_numbers:
            print(f"\n🎯 Solving Problem #{problem_num}")
            print("-" * 30)
            
            if problem_num not in problems:
                print(f"❌ Problem #{problem_num} not found!")
                failed_count += 1
                wrong_solutions.append(problem_num)
                continue
            
            try:
                problem = problems[problem_num]
                print(f"📋 Description: {problem['description']}")
                
                # Get initial state and target
                initial_state = {
                    1: problem["initial_state"]["1"],
                    2: problem["initial_state"]["2"], 
                    3: problem["initial_state"]["3"]
                }
                target = problem["target"]
                
                print(f"📋 Initial state: Rod 1 = {initial_state[1]}, Rod 2 = {initial_state[2]}, Rod 3 = {initial_state[3]}")
                print(f"🎯 Target rod: {target}")
                
                # Solve the problem
                seq = compute_full_sequence(initial_state, target)
                
                if seq:
                    print(f"📊 Total moves: {len(seq)}")
                    # Save solution
                    if save_solution(initial_state, target, seq):
                        print(f"✅ Problem #{problem_num} solved and saved!")
                        solved_count += 1
                        correct_solutions.append(problem_num)
                    else:
                        print(f"❌ Failed to save solution for Problem #{problem_num}!")
                        failed_count += 1
                        wrong_solutions.append(problem_num)
                else:
                    failed_count += 1
                    wrong_solutions.append(problem_num)
                    print(f"❌ Failed to solve Problem #{problem_num}: {problem['description']}")
                    
            except Exception as e:
                failed_count += 1
                wrong_solutions.append(problem_num)
                print(f"❌ Error solving Problem #{problem_num}: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SOLVING SUMMARY")
        print("=" * 60)
        print(f"✅ Solved: {solved_count} ->    ({', '.join(correct_solutions)})")
        print(f"❌ Failed: {failed_count} ->    ({', '.join(wrong_solutions)})")
        success_rate = (solved_count/(solved_count+failed_count))*100 if (solved_count+failed_count) > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if failed_count == 0:
            print("\n🎉 All problems solved successfully!")
        else:
            print(f"\n⚠️  {failed_count} problem(s) failed to solve!")
            
    except FileNotFoundError:
        print("❌ problems.json file not found!")
    except json.JSONDecodeError:
        print("❌ Invalid JSON format in problems.json!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("🔧 Hanoi Tower Problem Solver")
        print("=" * 40)
        print("Usage: python solve_problems.py <problem_numbers>...")
        print("Example: python solve_problems.py 1 2 3")
        print("\nAvailable options:")
        print("  • Specific numbers: python solve_problems.py 1 3 5")
        print("  • All problems: python solve_problems.py all")
        print("  • Range: python solve_problems.py 1-5")
        return
    
    args = sys.argv[1:]
    
    # Handle special cases
    if len(args) == 1:
        if args[0].lower() == "all":
            # Load all problems
            try:
                with open("problems.json", "r") as f:
                    data = json.load(f)
                if "problems" in data:
                    problem_numbers = list(data["problems"].keys())
                    print(f"Found {len(problem_numbers)} problems to solve")
                else:
                    print("❌ No problems found in problems.json!")
                    return
            except FileNotFoundError:
                print("❌ problems.json file not found!")
                return
            except json.JSONDecodeError:
                print("❌ Invalid JSON format in problems.json!")
                return
        elif "-" in args[0]:
            # Handle range like "1-5"
            try:
                start, end = map(int, args[0].split("-"))
                problem_numbers = [str(i) for i in range(start, end + 1)]
            except ValueError:
                print(f"❌ Invalid range format: {args[0]}!")
                print("Expected format: 1-5")
                return
        else:
            problem_numbers = args
    else:
        problem_numbers = args
    
    # Solve problems
    solve_problems(problem_numbers)

if __name__ == "__main__":
    main()
