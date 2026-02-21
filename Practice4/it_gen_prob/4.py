def squares(a, b):
    for i in range(a, b + 1):
        yield i * i
a, b = map(int, input().split())
for k in squares(a, b):
    print(k, end=" ")