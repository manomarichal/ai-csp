""" Command line interface to call the Sudoku solver. """
from enum import Enum

from typer import Typer
from tqdm import tqdm

from Sudoku import Sudoku
from NQueens import NQueens

# IMPORTANT: Do not edit this file!


class Method(str, Enum):
    bf = "bf"
    fc = "fc"
    ac3 = "ac3"


app = Typer()


def solve(csp, method: Method, initialAssignment=dict()):
    output_file = open("/home/mano/PycharmProjects/csp/results_temp.txt", "w")
    check = True
    if method == Method.bf:
        # print("Solving with brute force")
        assignment = csp.solveBruteForce(initialAssignment)
    elif method == Method.fc:
        # print("Solving with forward checking")
        assignment = csp.solveForwardChecking(initialAssignment)
    elif method == Method.ac3:
        # print("Solving with forward checking and ac3")
        assignment = csp.solveAC3(initialAssignment)
    else:
        check = False

    if check:
        output_file.write(str(csp.counter) + ' ')
        output_file.close()
    else:
        raise RuntimeError(f"Method '{method}' not found.")

    if assignment:
        s = csp.assignmentToStr(assignment)
        # tqdm.write("\nSolution:")
        # tqdm.write(s)
    else:
        tqdm.write("No solution found")


@app.command()
def sudoku(path: str, method: Method = Method.bf):
    """ Solve Sudoku as a CSP. """
    csp = Sudoku()
    initialAssignment = csp.parseAssignment(path)
    solve(csp, method, initialAssignment)

@app.command()
def queens(n: int = 5, method: Method = Method.bf):
    """ Solve the N Queens problem as a CSP. """
    csp = NQueens(n=n)
    solve(csp, method)

if __name__ == "__main__":
    app()
