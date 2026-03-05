import re
with open("raw.txt", "r", encoding="utf-8") as file:
    text = file.read()
dt = re.search("Время:\\s*(\\d{2}\\.\\d{2}\\.\\d{4})\\s+(\\d{2}:\\d{2}:\\d{2})", text)
if dt:
    date = dt.group(1)
    time = dt.group(2)
else:
    date = ""
    time = ""

pay = re.search("(Банковская карта|Наличные):", text)
if pay:
    payment_method = pay.group(1)
else:
    payment_method = ""

total_match = re.search("ИТОГО:\\s*\\n([\\d ]+,\\d{2})", text)
if total_match:
    total = total_match.group(1).replace(" ", "")
else:
    total = ""

pattern = "\\d+\\.\\s*\n(.*?)\n\\d+,\\d{3}\\s*x\\s*[\\d ]+,\\d{2}\n([\\d ]+,\\d{2})"
items = re.findall(pattern, text, re.DOTALL)
print("Products:")
for i, item in enumerate(items, 1):
    name = " ".join(item[0].split())
    price = item[1].replace(" ", "")
    print(i, "-", name, "-", price)
print("Date:", date)
print("Time:", time)
print("Payment method:", payment_method)
print("Total:", total)