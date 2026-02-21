import math
n = int(input("Number of sides: "))
l = float(input("Length of a side: "))
print("Area:", n * l * l / (4 * math.tan(math.pi/n)))
