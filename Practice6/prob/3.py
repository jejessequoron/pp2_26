from functools import reduce
l = [1, 2, 3, 4, 5]
print("The list of nums:", l)

sq = list(map(lambda x: x * x, l))
print("Squares:", sq)

e = list(filter(lambda x: x % 2 == 0, l))
print("Even numbers:", e)
o = list(filter(lambda x: x % 2 != 0, l))
print("Odd numbers:", o)

s = reduce(lambda a, b: a + b, l)
print("Sum:", s)
p = reduce(lambda a, b: a * b, l)
print("Product:", p)

a = ["apple", "banana", "cherry"]
print("\nEnumerate:")
for i, k in enumerate(a):
    print(f"{i}. {k}")

b = [100, 200, 300]
print("\nZip:")
for k, v in zip(a, b):
    print(k, v)

x = "123"
y = 45.6

print("\nType checking:")
print(type(x))
print(type(y))

print("\nConversions:")
print(int(x))
print(str(y))
print(float(x))