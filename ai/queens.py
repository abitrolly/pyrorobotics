# Return a list of solutions to the n-queens problem on an
# n-by-width board.  A solved board is expressed as a list of
# column positions for queens, indexed by row.  Rows and columns are
# indexed from zero.
def n_queens(n, width):
    if n == 0:
        return [[]] # one solution, the empty list
    else:
        return add_queen(n-1, width, n_queens(n-1, width))

# Try all ways of adding a queen to a column of row new_row, returning
# a list of solutions.  previous_solutions must be a list of new_row-queens
# solutions.
def add_queen(new_row, width, previous_solutions):
    solutions = []
    for sol in previous_solutions:
        # Try to place a queen on each column on row new_row.
        for new_col in range(width):
            # print 'trying', new_col, 'on row', new_row
            if safe_queen(new_row, new_col, sol):
                # No interference, so add this solution to the list.
                solutions.append(sol + [new_col])
    return solutions

# Is it safe to add a queen to sol at (new_row, new_col)?  Return
# true iff so.  sol must be a solution to the new_row-queens problem.
def safe_queen(new_row, new_col, sol):
    # Check against each piece on each of the new_row existing rows.
    for row in range(new_row):
        if (sol[row] == new_col or
            sol[row] + row == new_col + new_row or
            sol[row] - row == new_col - new_row):
            return 0
    return 1

for sol in n_queens(16, 16):
    print sol
