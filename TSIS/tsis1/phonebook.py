import csv
import json
from connect import get_con

conn = get_con()

def line():
    print("------------------------------------------------------")

def get_group_id(cur, group_name):
    group_name = group_name or "Other"
    cur.execute(
        """
        INSERT INTO groups(name)
        VALUES (%s)
        ON CONFLICT (name)
        DO UPDATE SET name = EXCLUDED.name
        RETURNING id
        """,
        (group_name,),
    )
    return cur.fetchone()[0]

def find_contact(cur, name):
    cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    return None

def save_contact(cur, contact, overwrite=False):
    name = contact["name"]
    contact_id = find_contact(cur, name)
    if contact_id and not overwrite:
        return "duplicate"
    group_id = get_group_id(cur, contact.get("group"))
    if contact_id:
        cur.execute(
            """
            UPDATE contacts
            SET surname = %s,
                email = %s,
                birthday = %s,
                group_id = %s
            WHERE id = %s
            """,
            (
                contact.get("surname"),
                contact.get("email"),
                contact.get("birthday") or None,
                group_id,
                contact_id,
            ),
        )
        cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
        status = "updated"
    else:
        cur.execute(
            """
            INSERT INTO contacts(name, surname, email, birthday, group_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                name,
                contact.get("surname"),
                contact.get("email"),
                contact.get("birthday") or None,
                group_id,
            ),
        )
        contact_id = cur.fetchone()[0]
        status = "inserted"
    for phone in contact.get("phones", []):
        cur.execute(
            """
            INSERT INTO phones(contact_id, phone, type)
            VALUES (%s, %s, %s)
            """,
            (contact_id, phone["phone"], phone["type"]),
        )
    return status

def print_contacts(rows):
    if not rows:
        print("No contacts found.")
        return
    print(f"\n{'ID':<5}{'NAME':<15}{'SURNAME':<15}{'EMAIL':<25}{'BIRTHDAY':<12}{'GROUP':<12}PHONES")
    for row in rows:
        birthday = row[4].isoformat() if row[4] else ""
        print(f"{row[0]:<5}{row[1]:<15}{row[2] or '':<15}{row[3] or '':<25}{birthday:<12}{row[5] or '':<12}{row[6] or ''}")

def select_contacts(where="", params=(), order_by="c.id", limit=None, offset=None):
    sql = f"""
        SELECT
            c.id,
            c.name,
            c.surname,
            c.email,
            c.birthday,
            g.name AS group_name,
            COALESCE(string_agg(p.type || ': ' || p.phone, ', ' ORDER BY p.id), '') AS phones
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        {where}
        GROUP BY c.id, g.name
        ORDER BY {order_by}
    """
    values = list(params)
    if limit is not None:
        sql += " LIMIT %s"
        values.append(limit)
    if offset is not None:
        sql += " OFFSET %s"
        values.append(offset)
    with conn.cursor() as cur:
        cur.execute(sql, values)
        return cur.fetchall()

def filter_by_group():
    group = input("Enter group: ")
    rows = select_contacts("WHERE g.name ILIKE %s", (f"%{group}%",))
    print_contacts(rows)
    line()

def search_by_email():
    email = input("Enter email part: ")
    rows = select_contacts("WHERE c.email ILIKE %s", (f"%{email}%",))
    print_contacts(rows)
    line()

def sort_contacts():
    print("1 - Sort by name")
    print("2 - Sort by birthday")
    print("3 - Sort by date added")
    choice = input("Choose: ")
    if choice == "1":
        rows = select_contacts(order_by="c.name")
    elif choice == "2":
        rows = select_contacts(order_by="c.birthday")
    elif choice == "3":
        rows = select_contacts(order_by="c.date_added")
    else:
        print("Invalid choice.")
        return
    print_contacts(rows)
    line()

def pag_nav():
    lim = int(input("Page size: "))
    ofs = 0
    while True:
        rows = select_contacts(limit=lim, offset=ofs)
        print_contacts(rows)
        command = input("\nnext / prev / quit: ").lower()
        if command == "next":
            ofs += lim
        elif command == "prev":
            ofs = max(0, ofs - lim)
        elif command == "quit":
            break
        else:
            print("Unknown command.")
    line()

def export_json():
    filename = input("JSON filename: ") or "contacts.json"
    contacts = []
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.id, c.name, c.surname, c.email, c.birthday, g.name
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            ORDER BY c.id
            """
        )
        for row in cur.fetchall():
            cur.execute(
                "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id",
                (row[0],),
            )
            phones = []
            for phone_row in cur.fetchall():
                phones.append({"phone": phone_row[0], "type": phone_row[1]})
            contacts.append(
                {
                    "name": row[1],
                    "surname": row[2],
                    "email": row[3],
                    "birthday": row[4].isoformat() if row[4] else "",
                    "group": row[5],
                    "phones": phones,
                }
            )
    with open(filename, "w") as f:
        json.dump(contacts, f, indent=4)
    print("Export completed.")
    line()

def import_json():
    filename = input("JSON filename: ")
    with open(filename) as f:
        contacts = json.load(f)
    with conn.cursor() as cur:
        for contact in contacts:
            if find_contact(cur, contact["name"]):
                answer = input(f"{contact['name']} exists. skip or overwrite? ")
                if answer.lower() != "overwrite":
                    continue
                save_contact(cur, contact, overwrite=True)
            else:
                save_contact(cur, contact)
        conn.commit()
    print("Import completed.")
    line()

def import_csv():
    with conn.cursor() as cur:
        with open("contacts.csv") as f:
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for row in reader:
                name, surname, email, birthday, group, phone, phone_type = row
                contact = {
                    "name": name,
                    "surname": surname,
                    "email": email,
                    "birthday": birthday,
                    "group": group,
                    "phones": [
                        {
                            "phone": phone,
                            "type": phone_type or "mobile",
                        }
                    ],
                }
                save_contact(cur, contact, overwrite=True)
        conn.commit()
    print("CSV import completed.")
    line()

def add_phone():
    name = input("Contact name: ")
    phone = input("New phone: ")
    phone_type = input("Type(home/work/mobile): ")
    with conn.cursor() as cur:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
        conn.commit()
    print("Phone added.")
    line()

def move_to_group():
    name = input("Contact name: ")
    group = input("New group: ")
    with conn.cursor() as cur:
        cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
    print("Contact moved.")
    line()

def search_contacts():
    query = input("Search query: ")
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        rows = cur.fetchall()
    print_contacts(rows)
    line()

def menu():
    while True:
        print("\nPHONEBOOK MENU")
        print("1 - Filter by group")
        print("2 - Search by email")
        print("3 - Sort contacts")
        print("4 - Paginated navigation")
        print("5 - Export to JSON")
        print("6 - Import from JSON")
        print("7 - Import from CSV")
        print("8 - Add phone")
        print("9 - Move to group")
        print("10 - Search contacts(name/email/phone)")
        print("0 - Exit")
        choice = input("Choose: ")
        if choice == "1":
            filter_by_group()
        elif choice == "2":
            search_by_email()
        elif choice == "3":
            sort_contacts()
        elif choice == "4":
            pag_nav()
        elif choice == "5":
            export_json()
        elif choice == "6":
            import_json()
        elif choice == "7":
            import_csv()
        elif choice == "8":
            add_phone()
        elif choice == "9":
            move_to_group()
        elif choice == "10":
            search_contacts()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")
menu()
conn.close()