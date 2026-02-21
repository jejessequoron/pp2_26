def g(n):
    for i in range(n):
        yield (i + 1) ** 2
n = int(input())
for k in g(n):
    print(k, end=" ")