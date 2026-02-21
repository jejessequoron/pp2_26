import datetime
def drop_ms(d: datetime):
    d = d.replace(microsecond=0)
    return d
d = datetime.datetime.now()
print(drop_ms(d))