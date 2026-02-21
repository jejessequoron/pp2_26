def g(n):
    for i in range(0, n + 1, 12):
        yield i
n = int(input())
for k in g(n):
    print(k, end=" ")