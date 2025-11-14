import math
from utils import simplify_sequence


def compute_move_transition(n, s, f, m):
    '''
    Input:
        - n: the total number of rings
        - s: the number of the start rod
        - f: the number of the final rod
        - m: the number of the move of which I want to calculate the associated transition (xm, ym)
    Output:
        - r: the number of the ring that moves during the transition
        - x: the number of the rod from which the transition of move m starts
        - y: the number of the rod to which the transition of move m ends
    Other variables:
        - d: the moving direction of the rings (-1 for going left and +1 for going right)
        - k: the number of transitions right before move m, that happened using the r ring
    '''
    r = ((2 * m) & -(2 * m)).bit_length() - 1
    d = (-1)**(n % 2 + (f - s) % 3)
    k = m / 2**r - 0.5
    x = 1 + (s + d * k * (2 - r % 2) - 1) % 3
    y = 1 + (x + d * (2 - r % 2) - 1) % 3
    return r, x, y

def compute_full_sequence(rods, target):
    '''
    Input:
        - rods: a dictionary, in the form {1: <list>, 2: <list>, 3: <list>}
            - 1: the initial state of the first (left) rod, represented as a list of rings ordered from bottom to top
            - 2: the initial state of the second (middle) rod, represented as a list of rings ordered from bottom to top
            - 3: the initial state of the third (right) rod, represented as a list of rings ordered from bottom to top
        - target: the number of the target rod
    Output:
        - seq: a dictionary, in the form {m1: [r1, x1, y1], m2: [r2, x2, y2], ...}
            - m: the number of the move
            - r: the number of the ring that moves during the transition of move m
            - x: the number of the rod from which the transition of move m starts
            - y: the number of the rod to which the transition of move m ends
    '''
    r1, r2, r3 = rods[1], rods[2], rods[3]
    r = r1 + r2 + r3
    n = len(r)
    rod_rings = list(rods.values())
    rings_places = n * [0]
    for i, rod in enumerate(rod_rings):
        for j in rod:
            rings_places[j - 1] = i + 1
    start = rings_places[0]
    seq = {}
    for m in range(1, 2**n):
        r, x, y = compute_move_transition(n, start, target, m)
        seq[m] = [int(r), int(x), int(y)]
    seq = simplify_sequence(seq)
    return seq
