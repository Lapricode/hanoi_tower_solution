#!/usr/bin/env python3
import json
from calculate_solution import compute_full_sequence
from utils import save_solution


def solve_all_problems():
    """Solve all problems in problems.json and save solutions"""
    try:
        # Load problems
        with open("problems.json", "r") as f:
            data = json.load(f)
        
        if "problems" not in data:
            print("❌ No problems found in problems.json!")
            return
        
        problems = data["problems"]
        print(f"🔧 Solving {len(problems)} problems...")
        
        solved_count = 0
        failed_count = 0
        
        for problem_num, problem in problems.items():
            try:
                print(f"🎯 Solving Problem {problem_num}: {problem['description']}")
                
                # Get initial state and target
                initial_state = {
                    1: problem["initial_state"]["1"],
                    2: problem["initial_state"]["2"], 
                    3: problem["initial_state"]["3"]
                }
                target = problem["target"]
                
                # Solve the problem
                seq = compute_full_sequence(initial_state, target)
                
                if seq:
                    # Save solution
                    if save_solution(initial_state, target, seq):
                        solved_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1
                    print(f"❌ Failed to solve Problem {problem_num}: {problem['description']}")
                    
            except Exception as e:
                failed_count += 1
                print(f"❌ Error solving Problem {problem_num}: {e}")
        
        # Summary
        print("\n" + "="*50)
        print("📊 SOLVING SUMMARY")
        print("="*50)
        print(f"✅ Successfully solved: {solved_count}")
        print(f"❌ Failed to solve: {failed_count}")
        print(f"📈 Success Rate: {(solved_count/(solved_count + failed_count)*100):.1f}%")
        
        if failed_count == 0:
            print("\n🎉 All problems solved successfully!")
        else:
            print(f"\n⚠️  {failed_count} problem(s) failed to solve")
            
    except FileNotFoundError:
        print("❌ problems.json file not found!")
    except json.JSONDecodeError:
        print("❌ Invalid JSON format in problems.json!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    solve_all_problems()
