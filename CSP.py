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
        for value in self.orderDomain(assignment, domains, var):
            test_assignment = dict(assignment)
            test_assignment[var] = value
            if self.isValid(test_assignment):
                assignment[var] = value
                result = self._solveBruteForce(assignment, domains)
                if result is not None: return result
                assignment.pop(var)

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
        for var_value in self.orderDomain(assignment, domains, var):
            test_assignment = dict(assignment)
            test_assignment[var] = var_value
            if self.isValid(test_assignment):
                assignment[var] = var_value
                result = self._solveForwardChecking(assignment, self.forwardChecking(assignment, domains, var))
                if result is not None: return result
                assignment.pop(var)

    def forwardChecking(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]], variable: Optional[Variable] = None) -> Dict[Variable, Set[Value]]:
        """ Implement the forward checking algorithm from the theory lectures.

        :param domains: current domains.
        :param assignment: current assignment.
        :param variable: If not None, the variable that was just assigned (only need to check changes).
        :return: the new domains after enforcing all constraints.
        """
        # TODO mooiere manier vinden voor als var niet none is
        new_domains = dict(domains)
        if variable is None: variables_to_check = self.variables
        else: variables_to_check = [variable]
        for var in variables_to_check:
            for neighbor in self.neighbors(var):
                if assignment.get(var) is not None:
                    valid_values = []
                    for neighbor_value in domains.get(neighbor):
                        if self.isValidPairwise(var, assignment.get(var), neighbor, neighbor_value):
                            valid_values.append(neighbor_value)
                    new_domains[neighbor] = set(valid_values)
        return new_domains

    def selectVariable(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Variable:
        """ Implement a strategy to select the next variable to assign. """
        # return random.choice(list(self.remainingVariables(assignment)))
        var_to_return = None
        smallest_domain = float("inf")
        for var in self.variables:
            if assignment.get(var) is not None: continue
            if len(domains.get(var)) < smallest_domain:
                smallest_domain, var_to_return = len(domains.get(var)), var
        return var_to_return

    def orderDomain(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]], var: Variable) -> List[Value]:
        """ Implement a smart ordering of the domain values. """
        amount_val_removed = dict() # how many values were removed from domains for each value in the domain of var
        org_size = 0 # how many values are currently in all the domains
        for domain in domains.values():
            org_size += len(domain)
        for value in domains.get(var):
            temp_assignment = assignment.copy()
            temp_assignment[var] = value
            difference = org_size
            for domain in self.forwardChecking(temp_assignment, domains, var).values():
                difference -= len(domain)
            amount_val_removed[value] = difference

        # sort the dictionary by values, we want the value with the lowest difference first
        sort = sorted(amount_val_removed.items(), key=lambda x: x[1], reverse=False)
        return [tup[0] for tup in sort]
        # return list(domains[var])

    def solveAC3(self, initialAssignment: Dict[Variable, Value] = dict()) -> Optional[Dict[Variable, Value]]:
        """ Called to solve this CSP with forward checking and AC3.
            Initializes domains and calls `CSP::_solveAC3`. """
        domains = domainsFromAssignment(initialAssignment, self.variables)
        return self._solveAC3(initialAssignment, self.ac3(initialAssignment, self.forwardChecking(initialAssignment, domains)))

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
        for var_value in self.orderDomain(assignment, domains, var):
            test_assignment = dict(assignment)
            test_assignment[var] = var_value
            if self.isValid(test_assignment):
                assignment[var] = var_value
                result = self._solveAC3(assignment, self.ac3(assignment, self.forwardChecking(assignment, domains, var)))
                if result is not None: return result
                assignment.pop(var)

    def ac3(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Dict[Variable, Set[Value]]:
        """ Implement the AC3 algorithm from the theory lectures.
        :return: the new domains ensuring arc consistency.
        """
        # store all arcs in a queue
        arc_queue = []
        for variable in self.variables:
            for neighbor in self.neighbors(variable):
                if assignment.get(variable) is None and assignment.get(neighbor) is None:
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
                    if assignment.get(new_tail) is None and not (new_tail, tail) in arc_queue:
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
