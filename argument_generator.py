# Helper program that exists to generate arguments for testing in the argument prover. Spaghetti code, but still helpful

import os
import sys
import lxml.builder
import lxml.etree
import datetime

print("Generate an argument that can be read by the prover in .bram format. No verification is run within this "
      "generator on whether statement syntax is correct to be read by the main program.\n")

author = input("Author: ")
include_author = True
if author.strip() == "":
    include_author = False

location = os.path.dirname(sys.argv[0])
directory = ""
invalid_dir = True

while invalid_dir:
    directory = input(f"Directory for argument (default is {location}/arguments): ")
    if directory.strip() == "":
        directory = location + "/arguments"
    if os.path.isdir(directory):
        invalid_dir = False
    elif directory == location + "/arguments":
        print(directory, "not found. Creating default directory.")
        os.mkdir(directory)
        invalid_dir = False
    else:
        print("Directory not found.")


invalid_name = True
file_name = ""

while invalid_name:
    file_name = input("Name of generated file (leave out .bram): ").strip()
    if file_name == "":
        print("File name cannot be empty.")
    else:
        invalid_name = False

invalid_num = True
num_premises = ""

while invalid_num:
    num_premises = input("Number of premises: ").strip()
    if num_premises.isnumeric():
        num_premises = int(num_premises)
        if num_premises < 1:
            print("Number of premises must be positive.")
        else:
            invalid_num = False
    else:
        print("Invalid number input.")

invalid_num = True
num_goals = ""

while invalid_num:
    num_goals = input("Number of goals: ").strip()
    if num_goals.isnumeric():
        num_goals = int(num_goals)
        if num_goals < 1:
            print("Number of premises must be positive.")
        else:
            invalid_num = False
    else:
        print("Invalid number input.")

print("Symbols accepted to represent logical operations:\n"
      "NOT - ¬, !, ~\n"
      "AND - ∧, &, ^\n"
      "OR - ∨, |, v\n"
      "IMPLIES - →, $\n"
      "IFF - ↔, %\n")

print(num_premises, "premises will now be input. The program will accept any input string, "
                    "regardless of correctness for the prover.")
premises = []

for i in range(1, num_premises+1):
    invalid = True
    while invalid:
        new_prem = input(f"{i}: ").strip()
        if new_prem == "":
            print("Premise cannot be empty.")
        else:
            premises.append(new_prem)
            invalid = False

print(num_goals, "goals will now be input. The program will accept any input string, "
                 "regardless of correctness for the prover.")
goals = []

for i in range(1, num_goals+1):
    invalid = True
    while invalid:
        new_goal = input(f"{i}: ").strip()
        if new_goal == "":
            print("Goal cannot be empty.")
        else:
            goals.append(new_goal)
            invalid = False

E = lxml.builder.ElementMaker()
BRAM = E.bram
PROGRAM = E.program
VERSION = E.version
METADATA = E.metadata
AUTHOR = E.author
CREATED = E.created
PROOF = E.proof
ASSUMPTION = E.assumption
GOAL = E.goal
RAW = E.raw

meta = METADATA()
if include_author:
    meta.append(AUTHOR(author))
meta.append(CREATED(datetime.datetime.utcnow().replace(microsecond=0).isoformat()))

proof = PROOF(id="0")
for i in range(num_premises):
    proof.append(ASSUMPTION(
        RAW(premises[i]),
        linenum=f"{i}"
    ))
for i in range(num_goals):
    proof.append(GOAL(
        RAW(goals[i]),
        linenum=f"{i+num_premises}"
    ))

xml_doc = BRAM(
    PROGRAM("Argument Generator"),
    VERSION("1.0"),
    meta,
    proof
)

with open(directory + "/" + file_name + ".bram", 'w') as f:
    f.write(lxml.etree.tostring(xml_doc, pretty_print=True, xml_declaration=True, encoding="utf-8").decode('utf-8'))
