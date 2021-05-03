import os
import sys
import src.argument_parser as arg_p
from lxml import etree


def main():
    print("Prove or disprove an argument defined in a .bram file. All premises should be defined in assumption tags "
          "and all goals should be defined in goal tags within the proof with an id of 0.\n")

    location = os.path.dirname(sys.argv[0])
    directory = ""
    invalid_dir = True

    while invalid_dir:
        directory = input(f"Directory of argument file (default is {location}/arguments): ")
        if directory.strip() == "":
            directory = location + "/arguments"
        if os.path.isdir(directory):
            invalid_dir = False
        else:
            print("Directory not found.")

    invalid_name = True
    file_name = ""

    while invalid_name:
        file_name = input("Name of argument file (leave out .bram): ").strip()
        if os.path.isfile(f"{directory}/{file_name}.bram"):
            invalid_name = False
        else:
            print("File not found.")

    file_loc = f"{directory}/{file_name}.bram"
    try:
        ap = arg_p.ArgumentParser(file_loc)
    except ValueError:
        print("A statement was improperly formatted and could not be read in or no goals were given.")
        input("Please press enter to close the program.")
        return

    if len(ap.goals) == 1:
        xml_doc = ap.solve(0)
        with open(f"{directory}/{file_name}_proof.bram", 'w') as f:
            f.write(etree.tostring(xml_doc, pretty_print=True, xml_declaration=True, encoding="utf-8").decode('utf-8'))
        print(f"{file_name}_proof.bram has been generated in {directory}.")
        input("Please press enter to close the program.")
        return
    else:
        print(f"{len(ap.goals)} goals detected in the file. Proving or disproving each of them in separate files.")
        for i in range(len(ap.goals)):
            xml_doc = ap.solve(i)
            with open(f"{directory}/{file_name}_proof_{i}.bram", 'w') as f:
                f.write(
                    etree.tostring(xml_doc, pretty_print=True, xml_declaration=True, encoding="utf-8").decode('utf-8'))
            print(f"{file_name}_proof_{i}.bram has been generated in {directory}.")
        input("Please press enter to close the program.")
        return


if __name__ == '__main__':
    main()
