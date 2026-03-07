import os
import shutil
with open("jdan.txt", "x") as f:
    f.write("This is some text file\n")
    f.write("I'll use it for my practice exercises\n")
    f.write("I don't know what to write\n")
    f.write("WHEN WE ALL FALL ASLEEP, WHERE DO WE GO?\n")
    f.write("HIT ME HARD AND SOFT\n")
    f.write("happier than ever\n")

f = open("jdan.txt")
print(f.read())
f.close()

with open("jdan.txt", "a") as f:
    f.write("\nBillie Eilish has won 10 grammys\n")
    f.write("And she's only 24\n")
with open("jdan.txt") as f:
    print(f.read())

shutil.copy("jdan.txt", "jdan_copy.txt")
shutil.copy("jdan.txt", "jdan_backup.txt")
print("Copied and backed up")

if os.path.exists("jdan_copy.txt"):
    os.remove("jdan_copy.txt")
    print("jdan_copy.txt deleted")
else:
    print("such file does not exist")