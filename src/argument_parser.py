from lxml import etree, builder
import logical_statements as ls
import datetime


def parse_file(file_loc):
    with open(file_loc) as fobj:
        xml = fobj.read()

    bram = etree.fromstring(bytes(xml, encoding='utf-8'))
    # Find the proof tag that will hold all assumptions and goals
    proof = next(bram.getiterator(tag="proof"))

    premises_raw = []
    goals_raw = []

    # Populate raw premises and raw goals
    for statement in proof.getchildren():
        text = next(statement.getiterator(tag="raw")).text
        if statement.tag == "assumption":
            premises_raw.append(text)
        else:
            goals_raw.append(text)

    return premises_raw, goals_raw


# Takes an index in a statement where ( is and returns the index where its corresponding ) is
def find_end_of_paren(statement, index):
    if statement[index] != '(':
        return index
    num = 1
    index += 1
    while num > 0:
        if statement[index] == '(':
            num += 1
        elif statement[index] == ')':
            num -= 1
        index += 1
        if index == len(statement) and num > 0:
            raise ValueError("Improper layout of parentheses")
    return index - 1


# Recursive method used to parse logical statement strings into objects. It works by determining the very last
# operation that will be performed in its given statement, turning that operation into its corresponding object,
# then recursing on the left and right-hand sides of that operation.
def parse_rec(statement):
    if len(statement) == 0:
        raise ValueError("Improper equation format")

    # Remove outer parentheses
    has_outer = statement[0] == '('
    while has_outer:
        index = find_end_of_paren(statement, 0)
        if index == len(statement)-1:
            statement = statement[1:-1]
        else:
            has_outer = False

    # Create list of all outer operations (operations not enclosed by parentheses)
    index = 0
    ops = []
    op_locs = []
    while index < len(statement):
        if statement[index] in ('!', '&', '|', '$', '%'):
            ops.append(statement[index])
            op_locs.append(index)
        elif statement[index] == '(':
            index = find_end_of_paren(statement, index)
        index += 1

    # If there are no outer operations found, return as a value (or raise an error)
    if len(ops) == 0:
        if '(' in statement or ')' in statement or '!' in statement or '&' in statement or '|' in statement or '$' in statement or '%' in statement:
            raise ValueError("Improper equation format")
        return ls.Value(statement)

    # Determine last outer operation
    if '%' in ops:
        index = op_locs[len(ops) - 1 - ops[::-1].index('%')]
        oper = '%'
    elif '$' in ops:
        index = op_locs[len(ops) - 1 - ops[::-1].index('$')]
        oper = '$'
    elif '|' in ops:
        index = op_locs[len(ops) - 1 - ops[::-1].index('|')]
        oper = '|'
    elif '&' in ops:
        index = op_locs[len(ops) - 1 - ops[::-1].index('&')]
        oper = '&'
    else:
        index = op_locs[len(ops) - 1 - ops[::-1].index('!')]
        oper = '!'

    # Recurse on operation type
    if oper == '%':
        return ls.Iff(parse_rec(statement[:index]), parse_rec(statement[index+1:]))
    if oper == '$':
        return ls.Implies(parse_rec(statement[:index]), parse_rec(statement[index+1:]))
    if oper == '|':
        return ls.Or(parse_rec(statement[:index]), parse_rec(statement[index+1:]))
    if oper == '&':
        return ls.And(parse_rec(statement[:index]), parse_rec(statement[index+1:]))
    return ls.Not(parse_rec(statement[index+1:]))


# Symbols accepted to represent logical operations:
# NOT - ¬, !, ~
# AND - ∧, &, ^
# OR - ∨, |, v
# IMPLIES - →, $
# IFF - ↔, %
def parse_statement(statement):
    statement = statement.strip()
    statement = statement.replace(" ", "")
    statement = statement.replace("¬", "!")
    statement = statement.replace("~", "!")
    statement = statement.replace("∧", "&")
    statement = statement.replace("^", "&")
    statement = statement.replace("∨", "|")
    statement = statement.replace("v", "|")
    statement = statement.replace("→", "$")
    statement = statement.replace("↔", "%")

    if statement.count('(') != statement.count(')'):
        raise ValueError("Improper number of parentheses")

    return parse_rec(statement)


class ArgumentParser:
    def __init__(self, file_loc):
        self.premises = []
        self.goals = []
        self.proof_num = 0
        self.linenum = 0

        # Get the raw statement strings from the given file
        premises_raw, goals_raw = parse_file(file_loc)

        if len(goals_raw) == 0:
            raise ValueError("Cannot have 0 goals")

        # Convert statement strings to logical objects
        for raw_premise in premises_raw:
            self.premises.append(parse_statement(raw_premise))
        for raw_goal in goals_raw:
            self.goals.append(parse_statement(raw_goal))

    def solve(self, index):
        self.proof_num = 1
        self.linenum = 0

        # Set up XML document
        E = builder.ElementMaker()
        BRAM = E.bram
        PROGRAM = E.program
        VERSION = E.version
        METADATA = E.metadata
        CREATED = E.created
        PROOF = E.proof
        ASSUMPTION = E.assumption
        RAW = E.raw

        meta = METADATA()
        meta.append(CREATED(datetime.datetime.utcnow().replace(microsecond=0).isoformat()))
        xml_doc = BRAM(
            PROGRAM("Argument Proof Generator"),
            VERSION("1.0"),
            meta
        )

        # Set up the assumptions
        init_proof = PROOF(id="0")
        for prem in self.premises:
            init_proof.append(ASSUMPTION(
                RAW(str(prem)),
                linenum=str(self.linenum)
            ))
            self.linenum += 1
        init_proof.append(ASSUMPTION(
            RAW(str(ls.Not(self.goals[index]))),
            linenum=str(self.linenum)
        ))
        self.linenum += 1
        xml_doc.append(init_proof)

        # Create active list. This list will hold all atomic statements (so A or !A) as well as all statements that
        # have not yet been broken down
        active = self.premises.copy()
        active.append(ls.Not(self.goals[index]))
        i = 0
        for a in active:
            active[i] = (a, i)
            i += 1

        # Begin the recursive algorithm for truth trees
        self.solve_rec(active, xml_doc, init_proof)

        return xml_doc

    # Recursive function to handle heavy lifting of truth tree methods
    def solve_rec(self, active, xml_doc, proof):
        E = builder.ElementMaker()
        STEP = E.step
        RAW = E.raw
        RULE = E.rule
        PREMISE = E.premise
        PROOF = E.proof

        # Handle all active statements that will not branch
        i = 0
        to_remove = []
        for a in active:
            if not a[0].will_branch():
                statements, rule = a[0].breakdown()
                for statement in statements[0]:
                    proof.append(STEP(
                        RAW(str(statement)),
                        RULE(rule),
                        PREMISE(str(a[1])),
                        linenum=str(self.linenum)
                    ))
                    active.append((statements[0][0], self.linenum))
                    self.linenum += 1
                to_remove.append(i)
            i += 1

        # Remove statements that were broken down from active
        for ind in to_remove[::-1]:
            del(active[ind])

        # Check if branch is closed
        closed = False
        c1 = 0
        c2 = 0
        # i and j both finished?
        for i in range(len(active)):
            if active[i][0].finished():
                for j in range(i+1, len(active)):
                    if active[j][0].finished():
                        # Only interested in comparing Nots vs. Values
                        if isinstance(active[i][0], ls.Value) == isinstance(active[j][0], ls.Value):
                            continue
                        # i corresponds to Value
                        if isinstance(active[i][0], ls.Value):
                            if active[i][0].interior[0] == active[j][0].interior[0].interior[0]:
                                closed = True
                                c1 = active[i][1]
                                c2 = active[j][1]
                        # i corresponds to Not
                        else:
                            if active[j][0].interior[0] == active[i][0].interior[0].interior[0]:
                                closed = True
                                c1 = active[i][1]
                                c2 = active[j][1]
        # If closed, note that in XML and return true
        if closed:
            proof.append(STEP(
                RULE("CLOSED-END"),
                PREMISE(str(c1)),
                PREMISE(str(c2)),
                linenum=str(self.linenum)
            ))
            self.linenum += 1
            return True

        # Check if all active statements cannot be broken down
        finished = True
        for a in active:
            if not a[0].finished():
                finished = False
        # If finished and wasn't closed, must be open, so note that in XML and return false
        if finished:
            proof.append(STEP(
                RULE("OPEN-END"),
                linenum=str(self.linenum)
            ))
            self.linenum += 1
            return False

        # Start next branch
        branch = STEP(
            RULE("BRANCH"),
            PREMISE(str(self.proof_num)),
            linenum=str(self.linenum)
        )
        # Create new proof for new branch
        pr1 = PROOF(id=str(self.proof_num))
        pr1_num = self.proof_num
        self.proof_num += 1
        self.linenum += 1
        proof.append(branch)

        # Break down first unfinished active statement
        next_ind = 0
        while active[next_ind][0].finished():
            next_ind += 1
        statements, rule = active[next_ind][0].breakdown()

        # Set up branch 1
        active1 = active.copy()
        for statement in statements[0]:
            active1.append((statement, self.linenum))
            pr1.append(STEP(
                RAW(str(statement)),
                RULE(rule),
                PREMISE(str(active[next_ind][1])),
                linenum=str(self.linenum)
            ))
            self.linenum += 1
        del(active1[next_ind])

        # Recurse on branch 1
        xml_doc.append(pr1)
        closed = self.solve_rec(active1, xml_doc, pr1)
        # If recursion found an open branch, propagate that upwards
        if not closed:
            proof.append(STEP(
                RULE("OPEN"),
                PREMISE(str(pr1_num)),
                linenum=str(self.linenum)
            ))
            self.linenum += 1
            return False

        # Set up branch 2
        pr2 = PROOF(id=str(self.proof_num))
        pr2_num = self.proof_num
        self.proof_num += 1
        branch.append(PREMISE(str(pr2_num)))

        active2 = active.copy()
        for statement in statements[1]:
            active2.append((statement, self.linenum))
            pr2.append(STEP(
                RAW(str(statement)),
                RULE(rule),
                PREMISE(str(active[next_ind][1])),
                linenum=str(self.linenum)
            ))
            self.linenum += 1
        del (active2[next_ind])

        # Recurse on branch 2
        xml_doc.append(pr2)
        closed = self.solve_rec(active2, xml_doc, pr2)
        # If recursion found an open branch, propagate that upwards
        if not closed:
            proof.append(STEP(
                RULE("OPEN"),
                PREMISE(str(pr2_num)),
                linenum=str(self.linenum)
            ))
            self.linenum += 1
            return False

        # If recursion found only closed branches, note that and return true
        proof.append(STEP(
            RULE("CLOSED"),
            PREMISE(str(pr1_num)),
            PREMISE(str(pr2_num)),
            linenum=str(self.linenum)
        ))
        self.linenum += 1
        return True
