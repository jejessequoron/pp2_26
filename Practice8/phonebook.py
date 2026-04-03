import psycopg2
from config import load_config

config = load_config()
conn = psycopg2.connect(**config)

def ins_upd():
    name = input("Enter name: ")
    surname = input("Enter surname: ")
    phone = input("Enter phone: ")
    with conn.cursor() as cur:
        cur.execute("CALL ins_upd_user(%s, %s, %s)", (name, surname, phone))
        conn.commit()
    print("User inserted or updated.")
    print('------------------------------------------------------')

def search_pat():
    pattern = input("Enter search pattern: ")
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_pat(%s)", (pattern,))
        rows = cur.fetchall()
    if rows:
        print(f"\n{'ID':<5}{'NAME':<15}{'SURNAME':<15}{'PHONE'}")
        for row in rows:
            print(f"{row[0]:<5}{row[1]:<15}{row[2]:<15}{row[3]}")
    else:
        print("No matching records found.")
    print('------------------------------------------------------')

def ins_many():
    n = int(input("How many users do you want to insert? "))
    names = []
    surnames = []
    phones = []
    for _ in range(n):
        name = input("Enter name: ")
        surname = input("Enter surname: ")
        phone = input("Enter phone: ")
        names.append(name)
        surnames.append(surname)
        phones.append(phone)
    with conn.cursor() as cur:
        cur.execute("CALL ins_many_users(%s, %s, %s)", (names, surnames, phones))
        conn.commit()
    print("Bulk insert finished. Check database NOTICE for incorrect data.")
    print('------------------------------------------------------')

def show_pag():
    limit = int(input("Enter LIMIT: "))
    offset = int(input("Enter OFFSET: "))
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM gpp(%s, %s)", (limit, offset))
        rows = cur.fetchall()
    if rows:
        print(f"\n{'ID':<5}{'NAME':<15}{'SURNAME':<15}{'PHONE'}")
        for row in rows:
            print(f"{row[0]:<5}{row[1]:<15}{row[2]:<15}{row[3]}")
    else:
        print("No data found.")
    print('------------------------------------------------------')

def del_user():
    value = input("Enter name or phone to delete: ")
    with conn.cursor() as cur:
        cur.execute("CALL del_user(%s)", (value,))
        conn.commit()
    print("Delete completed.")
    print('------------------------------------------------------')

def menu():
    while True:
        print("\nPHONEBOOK MENU")
        print("1 - Insert or update one user")
        print("2 - Search by pattern")
        print("3 - Insert many users")
        print("4 - Show paginated data")
        print("5 - Delete by name or phone")
        print("0 - Exit")
        ch = input("\nEnter choice: ")
        if ch == "1":
            ins_upd()
        elif ch == "2":
            search_pat()
        elif ch == "3":
            ins_many()
        elif ch == "4":
            show_pag()
        elif ch == "5":
            del_user()
        elif ch == "0":
            print("\nBye bye!")
            break
        else:
            print("INVALID CHOICE.")

menu()
conn.close()