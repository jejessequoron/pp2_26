import datetime
d1 = input("Enter datetime (YYYY-MM-DD HH:MM:SS): ")
d1 = datetime.datetime.strptime(d1, "%Y-%m-%d %H:%M:%S")
d2 = input("Enter datetime (YYYY-MM-DD HH:MM:SS): ")
d2 = datetime.datetime.strptime(d2, "%Y-%m-%d %H:%M:%S")
print("Difference in seconds: ", (d1 - d2).total_seconds())