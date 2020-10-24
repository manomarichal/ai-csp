import random
from typing import Set, Dict, List, TypeVar, Optional
from abc import ABC, abstractmethod
from util import monitor


Value = TypeVar('Value')


class Variable(ABC):
    @property
    @abstractmethod
    def startDomain(self) -> Set[Value]:
        """ Returns the set of initial values of this variable (not taking constraints into account). """
        pass


class CSP(ABC):
    counter = 0
    @property
    @abstractmethod
    def variables(self) -> Set[Variable]:
        """ Return the set of variables in this CSP.
            Abstract method to be implemented for specific instances of CSP problems.
        """
        pass

    def remainingVariables(self, assignment: Dict[Variable, Value]) -> Set[Variable]:
        """ Returns the variables not yet assigned. """
        return self.variables.difference(assignment.keys())

    @abstractmethod
    def neighbors(self, var: Variable) -> Set[Variable]:
        """ Return all variables related to var by some constraint.
            Abstract method to be implemented for specific instances of CSP problems.
        """
        pass

    def assignmentToStr(self, assignment: Dict[Variable, Value]) -> str:
        """ Formats the assignment of variables for this CSP into a string. """
        s = ""
        for var, val in assignment.items():
            s += f"{var} = {val}\n"
        return s

    def isComplete(self, assignment: Dict[Variable, Value]) -> bool:
        """ Return whether the assignment covers all variables.
            :param assignment: dict (Variable -> value)
        """
        return len(self.variables) == len(assignment) == len(set(assignment.keys()))

    @abstractmethod
    def isValidPairwise(self, var1: Variable, val1: Value, var2: Variable, val2: Value) -> bool:
        """ Return whether this pairwise assignment is valid with the constraints of the csp.
            Abstract method to be implemented for specific instances of CSP problems.
        """
        pass

    def isValid(self, assignment: Dict[Variable, Value]) -> bool:
        """ Return whether the assignment is valid (i.e. is not in conflict with any constraints).
            You only need to take binary constraints into account.
            Hint: use `CSP::neighbors` and `CSP::isValidPairwise` to check that all binary constraints are satisfied.
            Note that constraints are symmetrical, so you don't need to check them in both directions.
        """
        for var in assignment.keys():
            for neighbor in self.neighbors(var):
                if assignment.get(neighbor) is None:
                    continue
                elif not self.isValidPairwise(var, assignment[var], neighbor, assignment[neighbor]):
                    return False
        return True

    def _findUnassignedValue(self, assignment: Dict[Variable, Value]) -> Variable:
        for var in self.variables:
            if assignment.get(var) == None:
                return var

    def solveBruteForce(self, initialAssignment: Dict[Variable, Value] = dict()) -> Optional[Dict[Variable, Value]]:
        """ Called to solve this CSP with brute force technique.
            Initializes the domains and calls `CSP::_solveBruteForce`. """
        domains = domainsFromAssignment(initialAssignment, self.variables)
        return self._solveBruteForce(initialAssignment, domains)

    @monitor
    def _solveBruteForce(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Optional[Dict[Variable, Value]]:
        """ Implement the actual backtracking algorithm to brute force this CSP.
            Use `CSP::isComplete`, `CSP::isValid`, `CSP::selectVariable` and `CSP::orderDomain`.
            :return: a complete and valid assignment if one exists, None otherwise.
        """
        self.counter += 1
        if self.isComplete(assignment): return assignment
        var = self.selectVariable(assignment, domains)
        for value in domains.get(var):
            assignment[var] = value
            if self.isValid(assignment):
                result = self._solveBruteForce(assignment, domains)
                if result is not None: return result
        if assignment.get(var) is not None: assignment.pop(var)

    def solveForwardChecking(self, initialAssignment: Dict[Variable, Value] = dict()) -> Optional[Dict[Variable, Value]]:
        """ Called to solve this CSP with forward checking.
            Initializes the domains and calls `CSP::_solveForwardChecking`. """
        domains = domainsFromAssignment(initialAssignment, self.variables)
        domains = self.forwardChecking(initialAssignment, domains)
        return self._solveForwardChecking(initialAssignment, domains)

    @monitor
    def _solveForwardChecking(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Optional[Dict[Variable, Value]]:
        """ Implement the actual backtracking algorithm with forward checking.
            Use `CSP::forwardChecking` and you should no longer need to check if an assignment is valid.
            :return: a complete and valid assignment if one exists, None otherwise.
        """
        self.counter += 1
        if self.isComplete(assignment): return assignment
        var = self.selectVariable(assignment, domains)
        for var_value in domains.get(var):
            assignment[var] = var_value
            result = self._solveForwardChecking(assignment, self.forwardChecking(assignment, domains, var))
            if result is not None: return result
        if assignment.get(var) is not None: assignment.pop(var)

    def forwardChecking(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]], variable: Optional[Variable] = None) -> Dict[Variable, Set[Value]]:
        """ Implement the forward checking algorithm from the theory lectures.

        :param domains: current domains.
        :param assignment: current assignment.
        :param variable: If not None, the variable that was just assigned (only need to check changes).
        :return: the new domains after enforcing all constraints.
        """
        # TODO mooiere manier vinden voor als var niet none is
        new_domains = domains.copy()
        if variable is None: variables_to_check = self.variables
        else: variables_to_check = [variable]
        for var in variables_to_check:
            for neighbor in self.neighbors(var):
                if assignment.get(var) is None or assignment.get(neighbor) is not None: continue
                valid_values = []
                for neighbor_value in domains.get(neighbor):
                    if self.isValidPairwise(var, assignment.get(var), neighbor, neighbor_value):
                        valid_values.append(neighbor_value)
                new_domains[neighbor] = set(valid_values)
        return new_domains

    def selectVariable(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Variable:
        """ Implement a strategy to select the next variable to assign. """
        var_to_return = None
        smallest_domain = float("inf")
        for var in domains:
            if assignment.get(var) is not None: continue
            if len(domains.get(var)) < smallest_domain:
                smallest_domain, var_to_return = len(domains.get(var)), var
        domains[var_to_return] = set(self.orderDomain(assignment, domains, var_to_return))
        return var_to_return

    def orderDomain(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]], var: Variable) -> List[Value]:
        """ Implement a smart ordering of the domain values. """
        #TODO
        return list(domains[var])

    def solveAC3(self, initialAssignment: Dict[Variable, Value] = dict()) -> Optional[Dict[Variable, Value]]:
        """ Called to solve this CSP with forward checking and AC3.
            Initializes domains and calls `CSP::_solveAC3`. """
        domains = domainsFromAssignment(initialAssignment, self.variables)
        domains = self.ac3(initialAssignment, domains)
        return self._solveForwardChecking(initialAssignment, self.forwardChecking(initialAssignment, domains))

    @monitor
    def _solveAC3(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Optional[Dict[Variable, Value]]:
        """
            Implement the actual backtracking algorithm with AC3 (and FC).
            Use `CSP::ac3`.
            :return: a complete and valid assignment if one exists, None otherwise.
        """
        self.counter += 1
        if self.isComplete(assignment): return assignment
        var = self.selectVariable(assignment, domains)
        for var_value in domains.get(var):
            assignment[var] = var_value
            result = self._solveAC3(assignment, self.forwardChecking(assignment, domains))
            if result is not None: return result
        if assignment.get(var) is not None: assignment.pop(var)

    def ac3(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Dict[Variable, Set[Value]]:
        """ Implement the AC3 algorithm from the theory lectures.
        :return: the new domains ensuring arc consistency.
        """
        # store all arcs in a queue
        arc_queue = []
        for variable in self.variables:
            for neighbor in self.neighbors(variable):
                arc_queue.append((variable, neighbor))

        while len(arc_queue) > 0:
            tail, head = arc_queue.pop(0)
            values_removed = False

            # remove inconsistent values
            for v in domains.get(tail).copy():
                valid = False
                for w in domains.get(head):
                    if self.isValidPairwise(tail, v, head, w):
                        valid = True
                if not valid:
                    domains.get(tail).remove(v)
                    values_removed = True

            # add arcs if values were removed
            if values_removed:
                for new_tail in self.neighbors(tail):
                    if not (assignment.get(new_tail) or (new_tail, tail) in arc_queue) is None:
                        arc_queue.append((new_tail, tail))
        return domains


def domainsFromAssignment(assignment: Dict[Variable, Value], variables: Set[Variable]) -> Dict[Variable, Set[Value]]:
    """ Fills in the initial domains for each variable.
        Already assigned variables only contain the given value in their domain.
    """
    domains = {v: v.startDomain for v in variables}
    for var, val in assignment.items():
        domains[var] = {val}
    return domains
