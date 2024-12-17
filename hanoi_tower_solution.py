import math

# n is the total number of rings
# s is the number of the initial rod
# f is the number of the final rod
# m is the move's number of which I want to calculate the associated transition (xm, ym)
def calculate_move_transition(n, s, f, m):
    r = math.floor(math.log2(2 * m))  # initialize the number of the ring that moves during the transition
    while r >= 2:
        if (2 * m) % 2**r == 0:  # if 2 * m is divisible by 2**r
            break  # keep the current ring's number r
        r -= 1  # decrease the ring's number by 1
    d = (-1)**(n % 2 + (f - s) % 3)  # the moving direction of the rings (-1 for going left and +1 for going right)    
    k = m / 2**r - 0.5  # the number of transitions right before move m, that happened using the r ring
    xm = 1 + (s + d * k * (2 - r % 2) - 1) % 3  # the number of the rod from which the transition of move m starts
    ym = 1 + (xm + d * (2 - r % 2) - 1) % 3  # the number of the rod to which the transition of move m ends
    return r, xm, ym  # return r, xm, ym

if __name__ == "__main__":
    while True:
        n = int(input("\nGive the number of rings (type a natural number 1, 2, 3, ...): "))  # ask for the number of rings
        s = int(input("Give the initial rod (type 1, 2 or 3): "))  # ask for the number of the initial rod
        f = int(input("Give the final rod (type 1, 2 or 3): "))  # ask for the number of the final rod
        print()
        for m in range(1, 2**n):  # loop through all the moves of the optimal solve
            r, xm, ym = calculate_move_transition(n, s, f, m)  # calculate the transition of move m
            print(f"{m}:  {int(xm)} -> {int(ym)} ({int(r)})")  # print the results
