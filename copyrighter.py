import os, sys
from os.path import join, getsize

head: list[str]
with open("Copyright_and_notes", "r", encoding="utf-8") as f:
    head = f.readlines()

for root, dirs, files in os.walk("ii_constructor"):
    for name in files:
        filename = os.path.join(root, name)
        if filename[-3:] != '.py':
            continue

        lines = []
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()

        with open(filename, "w", encoding="utf-8") as f:
            for line in head:
                f.write("# " + line)

            f.write("\n\n\n")
        
        with open(filename, "a", encoding="utf-8") as f:
            skip = True

            for line in lines:
                if skip:
                    if line[0] == '#':
                        continue
                    else:
                        skip = False

                f.write(line)
