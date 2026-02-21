def g(n):
    for i in range(0, n + 1, 2):
        yield i
n = int(input())
gen = g(n)
for i in range(n // 2):
    print(next(gen), end=",")
print(next(gen))