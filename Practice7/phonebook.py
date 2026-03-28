import csv
import psycopg2
from config import load_config

config = load_config()
conn = psycopg2.connect(**config)
def createTable():
     command = """CREATE TABLE phb (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                phone VARCHAR(31)
            )"""
     with conn.cursor() as cur:
          cur.execute(command)
          conn.commit()

def insertConsole():
    nm = input("\nEnter contact name: ")
    ph = input("Enter contact phone number: ")
    command = 'insert into phb(name, phone) values(%s, %s)'
    with conn.cursor() as cur:
          cur.execute(command, (nm, ph))
          conn.commit()
    print(f'\nContact {nm} inserted.')
    print('------------------------------------------------------')

def insertCSV():
    command = 'insert into phb(name, phone) values(%s, %s)'
    with conn.cursor() as cur:
        with open('contacts.csv', "r") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            _ = next(csvreader)
            for row in csvreader:
                name, phone = row
                cur.execute(command, (name, phone))
        conn.commit()
    print('\nContact(s) from CSV file inserted')
    print('------------------------------------------------------')

def update():
     print('\n1 - To update name')
     print('2 - To update phone number')
     ch = input("\nChoose 1 or 2: ")
     nm = input('Enter current contact name: ')
     with conn.cursor() as cur:
          if ch=='1':
               new = input('Enter new name: ')
               command = 'update phb SET name = %s where name = %s'
               cur.execute(command, (new, nm))
               print('\nContact updated.')
          elif ch=='2':
               new = input('Enter new phone: ')
               command = 'update phb SET phone = %s where name = %s'
               cur.execute(command, (new, nm))
               print('\nContact updated.')
          else:
               print('\nINVALID CHOICE.')
          conn.commit()
     print('------------------------------------------------------')

def query():
     print('\n1 - To show all contacts')
     print('2 - To search contact by name')
     print('3 - To search contact by phone prefix')
     ch = input('\nChoose 1 or 2 or 3: ')
     with conn.cursor() as cur:
          if ch == '1':
               command = 'select * from phb'
               cur.execute(command)
          elif ch == '2':
               nm = input('Enter name(or its part): ')
               command = 'select * from phb where name ilike %s order by id'
               cur.execute(command, (f"%{nm}%",))
          elif ch == '3':
               pr = input('Enter phone prefix: ')
               command = 'select * from phb where phone like %s order by id'
               cur.execute(command, (f"{pr}%",))
          else:
               print('\nINVALID CHOICE.')
          rows = cur.fetchall()
          print('')
          if rows:
             print(f"{'ID':<5}{'name':<12}phone")
             for row in rows:
                print(f"{row[0]:<5}{row[1]:<12}{row[2]}")
          else:
             print("No contacts found.")
     print('------------------------------------------------------')

def delete():
    print("1 - Delete by name")
    print("2 - Delete by phone number")
    ch = input("Choose 1 or 2: ")
    with conn.cursor() as cur:
         if ch == '1':
              nm = input('Enter name: ')
              command = 'delete from phb where name = %s'
              cur.execute(command, (nm,))
              print("\nContact deleted.")
         elif ch == '2':
              ph = input('Enter phone number: ')
              command = 'delete from phb where phone = %s'
              cur.execute(command, (ph,))
              print("\nContact deleted.")
         else:
              print("Invalid choice.")
         conn.commit()
    print('------------------------------------------------------')

def menu():
     while True:
        print("\nPHONEBOOK MENU")
        print("1 - Insert from console")
        print("2 - Insert from CSV")
        print("3 - Update contact")
        print("4 - Query contacts")
        print("5 - Delete contact")
        print("0 - Exit")
        ch = input("\nEnter choice: ")
        if ch == "1":
            insertConsole()
        elif ch == "2":
            insertCSV()
        elif ch == "3":
            update()
        elif ch == "4":
            query()
        elif ch == "5":
            delete()
        elif ch == "0":
            print('''\n  Bye bye!     
                   
   ######
##      ##
##     ###
 #   #
  #   #
   #   #
    #    #
      #    #####
       ##        ##
         ##      ##
           #####
''')
            break
        else:
            print("INVALID CHOICE.")

createTable()
menu()
conn.close()