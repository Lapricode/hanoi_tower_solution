import math


# n is the total number of rings
# s is the number of the initial rod
# f is the number of the final rod
# m is the move's number of which I want to calculate the associated transition (xm, ym)
def calculate_move_transition(n, s, f, m):
    r = ((2 * m) & -(2 * m)).bit_length() - 1  # the ring's number that moves during the transition
    d = (-1)**(n % 2 + (f - s) % 3)  # the moving direction of the rings (-1 for going left and +1 for going right)
    k = m / 2**r - 0.5  # the number of transitions right before move m, that happened using the r ring
    xm = 1 + (s + d * k * (2 - r % 2) - 1) % 3  # the number of the rod from which the transition of move m starts
    ym = 1 + (xm + d * (2 - r % 2) - 1) % 3  # the number of the rod to which the transition of move m ends
    return r, xm, ym  # return r, xm, ym


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
