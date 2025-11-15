#!/usr/bin/env python3
import sys
import json
from utils import load_solution, verify_solution


def test_solutions(solution_numbers):
    """
    Test specified solutions by loading and verifying them
    
    Args:
        solution_numbers: list of solution numbers to test
    """
    if not solution_numbers:
        print("❌ No solution numbers provided!")
        print("Usage: python test_solutions.py 1 2 3 ...")
        return
    
    print(f"Testing {len(solution_numbers)} solution(s): {', '.join(solution_numbers)}")
    print("=" * 60)
    
    passed = 0
    failed = 0
    correct_solutions = []
    wrong_solutions = []
    
    for sol_num in solution_numbers:
        print(f"\n🔍 Testing Solution #{sol_num}")
        print("-" * 30)
        
        try:
            # Load solution
            initial_state, target, seq = load_solution("solutions.json", int(sol_num))
            
            if initial_state is None or target is None or seq is None:
                print(f"❌ Failed to load solution #{sol_num}!")
                failed += 1
                continue
            
            print(f"📋 Initial state: Rod 1 = {initial_state[1]}, Rod 2 = {initial_state[2]}, Rod 3 = {initial_state[3]}")
            print(f"🎯 Target rod: {target}")
            print(f"📊 Total moves: {len(seq)}")
            
            # Verify solution
            print("🔧 Verifying solution...")
            
            # Convert string keys to integers for verify_solution
            int_seq = {int(k): v for k, v in seq.items()}
            is_valid = verify_solution(initial_state, int_seq, target)
            
            if is_valid:
                print(f"✅ Solution #{sol_num} is VALID!")
                passed += 1
                correct_solutions.append(sol_num)
            else:
                print(f"❌ Solution #{sol_num} is INVALID!")
                failed += 1
                wrong_solutions.append(sol_num)
                
        except Exception as e:
            print(f"❌ Error testing solution #{sol_num}: {e}!")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed} ->    ({', '.join(correct_solutions)})")
    print(f"❌ Failed: {failed} ->    ({', '.join(wrong_solutions)})")
    success_rate = (passed/(passed+failed))*100 if (passed+failed) > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if failed == 0:
        print("\n🎉 All solutions are valid!")
    else:
        print(f"\n⚠️  {failed} solution(s) failed verification!")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("🔍 Hanoi Tower Solution Tester")
        print("=" * 40)
        print("Usage: python test_solutions.py <solution_numbers>...")
        print("Example: python test_solutions.py 1 2 3")
        print("\nAvailable options:")
        print("  • Specific numbers: python test_solutions.py 1 3 5")
        print("  • All solutions: python test_solutions.py all")
        print("  • Range: python test_solutions.py 1-5")
        return
    
    args = sys.argv[1:]
    
    # Handle special cases
    if len(args) == 1:
        if args[0].lower() == "all":
            # Load all solutions
            try:
                with open("solutions.json", "r") as f:
                    data = json.load(f)
                if "solutions" in data:
                    solution_numbers = list(data["solutions"].keys())
                    print(f"Found {len(solution_numbers)} solutions to test")
                else:
                    print("❌ No solutions found in solutions.json!")
                    return
            except FileNotFoundError:
                print("❌ solutions.json file not found!")
                return
            except json.JSONDecodeError:
                print("❌ Invalid JSON format in solutions.json!")
                return
        elif "-" in args[0]:
            # Handle range like "1-5"
            try:
                start, end = map(int, args[0].split("-"))
                solution_numbers = [str(i) for i in range(start, end + 1)]
            except ValueError:
                print(f"❌ Invalid range format: {args[0]}!")
                print("Expected format: 1-5")
                return
        else:
            solution_numbers = args
    else:
        solution_numbers = args
    
    # Test solutions
    test_solutions(solution_numbers)

if __name__ == "__main__":
    main()
