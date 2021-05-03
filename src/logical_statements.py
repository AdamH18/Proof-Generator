from abc import ABC, abstractmethod

'''
All logical operators as well as values are represented through the classes in here. The breakdown
function is used to provide branching values, finished says whether or not a statement can be
further broken down, and they are all convertible to strings.
'''


FITCH = True


class LogicalOperator(ABC):
    def __init__(self):
        self.interior = []

    '''
    The main driver function of truth tree branching. Each logical operator will return a list of lists
    of LogicalOperators. The outer list of either 1 or 2 lists determines whether there is any branching,
    and the inner list(s) of LogicalOperators are the statements taken as truth within that branch.
    '''
    @abstractmethod
    def breakdown(self):
        pass

    def finished(self):
        return False

    def will_branch(self):
        return True

    @abstractmethod
    def __str__(self):
        pass


class Value(LogicalOperator):
    def __init__(self, name):
        super().__init__()
        self.interior.append(name)

    def breakdown(self):
        pass

    def finished(self):
        return True

    def __str__(self):
        return self.interior[0]


class Not(LogicalOperator):
    def __init__(self, interior):
        super().__init__()
        self.interior.append(interior)

    def breakdown(self):
        if isinstance(self.interior[0], Not):
            return [[self.interior[0].interior[0]]], "Double Negation"
        elif isinstance(self.interior[0], And):
            return [[Not(self.interior[0].interior[0])], [Not(self.interior[0].interior[1])]], \
                   "Breakdown Negated Conjunction"
        elif isinstance(self.interior[0], Or):
            return [[Not(self.interior[0].interior[0]), Not(self.interior[0].interior[1])]], \
                   "Breakdown Negated Disjunction"
        elif isinstance(self.interior[0], Implies):
            return [[self.interior[0].interior[0], Not(self.interior[0].interior[1])]], "Breakdown Negated Conditional"
        elif isinstance(self.interior[0], Iff):
            return [[self.interior[0].interior[0], Not(self.interior[0].interior[1])],
                    [Not(self.interior[0].interior[0]), self.interior[0].interior[1]]], \
                   "Breakdown Negated Biconditional"

    def finished(self):
        return isinstance(self.interior[0], Value)

    def will_branch(self):
        return not (isinstance(self.interior[0], Or) or isinstance(self.interior[0], Implies) or isinstance(self.interior[0], Not))

    def __str__(self):
        int_val = str(self.interior[0])
        if isinstance(self.interior[0], Value) or isinstance(self.interior[0], Not):
            if FITCH:
                return f"~{int_val}"
            return f"¬{int_val}"
        if FITCH:
            return f"~({int_val})"
        return f"¬({int_val})"


class And(LogicalOperator):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.interior.append(lhs)
        self.interior.append(rhs)

    def breakdown(self):
        return [self.interior], "Breakdown Conjunction"

    def will_branch(self):
        return False

    def __str__(self):
        lhs_val = str(self.interior[0])
        rhs_val = str(self.interior[1])
        if not isinstance(self.interior[0], Value):
            lhs_val = f"({lhs_val})"
        if not isinstance(self.interior[1], Value):
            rhs_val = f"({rhs_val})"
        if FITCH:
            return f"{lhs_val}&{rhs_val}"
        return f"{lhs_val}∧{rhs_val}"


class Or(LogicalOperator):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.interior.append(lhs)
        self.interior.append(rhs)

    def breakdown(self):
        return [[self.interior[0]], [self.interior[1]]], "Breakdown Disjunction"

    def __str__(self):
        lhs_val = str(self.interior[0])
        rhs_val = str(self.interior[1])
        if not isinstance(self.interior[0], Value):
            lhs_val = f"({lhs_val})"
        if not isinstance(self.interior[1], Value):
            rhs_val = f"({rhs_val})"
        if FITCH:
            return f"{lhs_val}|{rhs_val}"
        return f"{lhs_val}∨{rhs_val}"


class Implies(LogicalOperator):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.interior.append(lhs)
        self.interior.append(rhs)

    def breakdown(self):
        return [[Not(self.interior[0])], [self.interior[1]]], "Breakdown Conditional"

    def __str__(self):
        lhs_val = str(self.interior[0])
        rhs_val = str(self.interior[1])
        if not isinstance(self.interior[0], Value):
            lhs_val = f"({lhs_val})"
        if not isinstance(self.interior[1], Value):
            rhs_val = f"({rhs_val})"
        if FITCH:
            return f"{lhs_val}${rhs_val}"
        return f"{lhs_val}→{rhs_val}"


class Iff(LogicalOperator):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.interior.append(lhs)
        self.interior.append(rhs)

    def breakdown(self):
        return [self.interior, [Not(self.interior[0]), Not(self.interior[1])]], "Breakdown Biconditional"

    def __str__(self):
        lhs_val = str(self.interior[0])
        rhs_val = str(self.interior[1])
        if not isinstance(self.interior[0], Value):
            lhs_val = f"({lhs_val})"
        if not isinstance(self.interior[1], Value):
            rhs_val = f"({rhs_val})"
        if FITCH:
            return f"{lhs_val}%{rhs_val}"
        return f"{lhs_val}↔{rhs_val}"
