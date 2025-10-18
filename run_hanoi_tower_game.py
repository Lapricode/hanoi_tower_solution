from hanoi_tower_solution import calculate_move_transition


if __name__ == "__main__":
    while True:
        try:
            n = int(input("\nGive the number of rings (type an integer greater than 1): "))  # ask for the number of rings
            if n <= 1:
                print("❌ The number of rings must be greater than 1.")
                continue
            s = int(input("Give the initial rod (type 1, 2 or 3): "))  # ask for the initial rod
            if s not in (1, 2, 3):
                print("❌ The initial rod must be 1, 2, or 3.")
                continue
            f = int(input("Give the final rod (type 1, 2 or 3): "))  # ask for the final rod
            if f not in (1, 2, 3):
                print("❌ The final rod must be 1, 2, or 3.")
                continue
            if s == f:  # check that initial and final rods are not the same
                print("❌ The initial and final rods must be different.")
                continue
            print()
            for m in range(1, 2**n):  # loop through all the moves of the optimal solution
                r, xm, ym = calculate_move_transition(n, s, f, m)
                print(f"{m}:  {int(xm)} -> {int(ym)} ({int(r)})")
        except ValueError:
            print("❌ Please enter valid integers only.")
        except KeyboardInterrupt:
            print("\nProgram terminated by user.")
            break
