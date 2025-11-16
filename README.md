# Tower of Hanoi Move Calculator

This code calculates the **Tower of Hanoi** optimal move sequence **without using recursion**. It determines each move directly from mathematical relations, providing an efficient and elegant **closed form solution**.

## Usage

### `compute_move_transition(n, s, f, m)`

The main mathematical core of the project, and building block for constructing the solutions (used by the `compute_full_sequence` function), avoiding the known slow recursive implementations. It calculates the transition for the **m-th move** in the Tower of Hanoi optimal sequence.

```bash
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
```

### `main`

To get the desired optimal game, run the main script with one of the following input methods:

**Classic mode** (default): All rings start on one rod and must move to target rod

```bash
python3 main.py
```

Enter:

- **Number of rings** (`n >= 1`)
- **Starting rod** (`1–3`)
- **Final rod** (`1–3`, different from starting one)

**Custom mode**: Specify rings for each rod individually

```bash
python3 main.py -im m
```

Enter:

- **Rings for each rod** (bottom to top, comma-separated)
- **Target rod** (`1–3`)

**Preset mode**: Select from predefined problems

```bash
python3 main.py -im p
```

Choose from available problems in `problems.json`.

**Save solutions**: Enable saving solutions to `solutions.json`

```bash
python3 main.py -s y
```

Combine with any input method:

```bash
python3 main.py -im m -s y
```

## Solution presentation:

The program prints the solution in the following format (for each one of the 2^n-1 moves):
move_number: from -> to (ring_number)

```bash
$ python3 main.py

Give the number of rings (type an integer greater than 1): 3
Give the starting rod (type 1, 2 or 3): 1
Give the final rod (type 1, 2 or 3): 3

1:  1 -> 3 (1)
2:  1 -> 2 (2)
3:  3 -> 2 (1)
4:  1 -> 3 (3)
5:  2 -> 1 (1)
6:  2 -> 3 (2)
7:  1 -> 3 (1)
```

## Additional Executables

### `solve_problems.py`

Solves specified problems from `problems.json` and saves solutions to `solutions.json`.

```bash
# Solve specific problems
python3 solve_problems.py 1 2 3

# Solve all problems
python3 solve_problems.py all

# Solve a range of problems
python3 solve_problems.py 1-5
```

### `test_solutions.py`

Tests saved solutions located in `solutions.json` to verify correctness.

```bash
# Test specific solutions
python3 test_solutions.py 1 2 3

# Test all solutions
python3 test_solutions.py all

# Test a range of solutions
python3 test_solutions.py 1-5
```

## Known Limitations

**Optimal Solutions:**

- **Classic configurations** (all rings starting on one rod): Solutions are guaranteed to be optimal
- **Custom configurations** (rings distributed across multiple rods): Solutions may not be optimal

The algorithm provides mathematically optimal solutions for the traditional Tower of Hanoi problem where all rings begin on a single rod. However, when rings are initially distributed across multiple rods (custom configurations), the generated solutions are valid but may not represent the shortest possible move sequence.
