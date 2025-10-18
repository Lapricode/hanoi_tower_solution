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
