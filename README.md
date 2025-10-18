# Tower of Hanoi Move Calculator

This code computes the **Tower of Hanoi** optimal move sequence **without using recursion**.

It determines each move directly from mathematical relations, providing an efficient and elegant closed form solution.

## Usage

To get the desired optimal game, run the main script and enter:

- **Number of rings** (`n >= 1`)
- **Initial rod** (`1–3`)
- **Final rod** (`1–3`, different from initial)

The program prints the solution in the following format (for each one of the 2\*\*n-1 moves):

move_number: from -> to (ring_number)
