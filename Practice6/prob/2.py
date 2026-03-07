import os
import shutil
os.makedirs("a/b/c", exist_ok=True)
print("Nested directories created")

with open("a/1.txt", "w") as f:
    f.write("text file")
with open("a/2.py", "w") as f:
    f.write("#python file")
with open("a/b/3.txt", "w") as f:
    f.write("another text file")

print("\nAll files and folders:")
for c in os.listdir("a"):
    print(c)

print("\nAll .txt files:")
for r, d, fs in os.walk("a"):
    for f in fs:
        if f.endswith(".txt"):
            print(os.path.join(r, f))

shutil.copy("a/1.txt", "a/b/1_copy.txt")
print("\n1.txt copied to b")

shutil.move("a/2.py", "a/b/2.py")
print("2.py moved to 2")