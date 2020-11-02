from typing import Set, Dict

from CSP import CSP, Variable, Value

class Sudoku(CSP):
    def __init__(self):
        super().__init__()
        self._variables = list(Cell(row, col) for col in range(9) for row in range(9))
        # TODO: Implement Sudoku::__init__ (problem 4)

    @property
    def variables(self) -> Set['Cell']:
        """ Return the set of variables in this CSP. """
        return set(self._variables)

    def getCell(self, x: int, y: int) -> 'Cell':
        """ Get the variable corresponding to the cell on (x, y) """
        return self._variables[x*9 + y]

    def neighbors(self, var: 'Cell') -> Set['Cell']:
        """ Return all variables related to var by some constraint. """
        neighbors = set()
        for cell in self.variables - {var}:
            if var.isNeighborOf(cell):
                neighbors.add(cell)
        return neighbors

    def isValidPairwise(self, var1: 'Cell', val1: Value, var2: 'Cell', val2: Value) -> bool:
        """ Return whether this pairwise assignment is valid with the constraints of the csp. """
        return not var2 in self.neighbors(var1) or val1 != val2

    def assignmentToStr(self, assignment: Dict['Cell', Value]) -> str:
        """ Formats the assignment of variables for this CSP into a string. """
        s = ""
        for y in range(9):
            if y != 0 and y % 3 == 0:
                s += "---+---+---\n"
            for x in range(9):
                if x != 0 and x % 3 == 0:
                    s += '|'

                cell = self.getCell(x, y)
                s += str(assignment.get(cell, ' '))
            s += "\n"
        return s

    def parseAssignment(self, path: str) -> Dict['Cell', Value]:
        """ Gives an initial assignment for a Sudoku board from file. """
        initialAssignment = dict()

        with open(path, "r") as file:
            for y, line in enumerate(file.readlines()):
                if line.isspace():
                    continue
                assert y < 9, "Too many rows in sudoku"

                for x, char in enumerate(line):
                    if char.isspace():
                        continue

                    assert x < 9, "Too many columns in sudoku"

                    var = self.getCell(x, y)
                    val = int(char)

                    if val == 0:
                        continue

                    assert val > 0 and val < 10, f"Impossible value in grid"
                    initialAssignment[var] = val
        return initialAssignment


class Cell(Variable):
    def __init__(self, row, col):
        super().__init__()
        self.value = -1
        self.row = row
        self.col = col
        self.square = int(row/3)*3 + int(col/3)

    @property
    def startDomain(self) -> Set[Value]:
        """ Returns the set of initial values of this variable (not taking constraints into account). """
        return set(range(9))

    def __repr__(self):
        return str(self.row) + '/' + str(self.col) + '/' + str(self.square)

    def isNeighborOf(self, cell:'Cell'):
        return self.square == cell.square or self.row == cell.row or self.col == cell.col
