import os
import time
import sqlite3
import pandas as pd
from tabulate import tabulate
from datetime import datetime

connection = sqlite3.connect("databases/library.db")
cursor = connection.cursor()

def authentication():
    os.system("clear")
    username, password = None, None
    while username != "admin" or password != "abc_def":
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        print("============================")
        
    menu()

def date_format(date_input):
    current_year = datetime.now().year
    try:
        date_object = datetime.strptime(date_input, "%Y%m%d")

        if date_object.year > current_year:
            print("Invalid Date")
        else:
            return date_object.strftime("%d-%m-%Y")
    
    except (ValueError, IndexError):
        return None 

def menu():
    os.system("clear")

    print("""
        ========================================
        Welcome to XYZ Library Management System
        ========================================
    """)

    options = {
        1: "Update Books",
        2: "Add Books",
        3: "Exit"
    }

    print("Choose from the following options: ")
    for i, j in options.items():
        print(f"{i}. {j}")

    user_choice = None
    while user_choice not in options:
        try: 
            user_choice = int(input("Enter your choice: "))
        except ValueError as e:
            print("Invalid input.")
            time.sleep(2)
            menu()

    match user_choice:
        case 1:
            update_books()
        case 2:
            enter_books()
        case 3, _:
            exit

def update_books():

    admin_preference = None

    print("""
          1. Delete Record(s).
          2. Correction.
          3. Update number of available copies. 
          4. View Database.
        """)

    while admin_preference not in [1, 2, 3, 4]:
        admin_preference = int(input("Enter your choice: "))

    if admin_preference == 1:
        id = int(input("Enter the ID for the record you wish to delete: "))
        cursor.execute(f'''
            select BOOK_NAME from books where ID = {id};
        ''')
        book_name = cursor.fetchall()[0][0]

        print(f"Deleting book {book_name} from the database.")

        cursor.execute(f'''
            delete from books where ID = {id};
        ''')

        time.sleep(3)

        connection.commit()

        menu()
        
    elif admin_preference == 2:
        rec = input ("Enter the id you wish to update: ")
        col = input ("Enter the column you wish to update: ")
        upcol = input ("Enter the updated value: ")
        cursor.execute(f'''
            update books set "{col}" = "{upcol}" where ID= {rec};
        ''')

        connection.commit()
        menu()

    elif admin_preference == 3:

        book_id = int(input("Enter the book id for which you'd like to update the available copies: "))

        cursor.execute(f'''
            select NUMBER_OF_COPIES_AVAILABLE from books where ID = {book_id}
        ''')
        rows = cursor.fetchone()[0]

        print(f"Current number of copies available: {rows} ")
        updated_copies = int(input("Enter updated value for 'number of available copies': "))
        cursor.execute(f'''
            update books set NUMBER_OF_COPIES_AVAILABLE = {updated_copies} where ID = {book_id};
        ''')

        connection.commit()

        menu()

    elif admin_preference == 4:
        proceed = None

        print ("""
                              ===================
                              Info on Table books
                              ===================
        """)
        cursor.execute('''
            select * from books;
        ''')
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns = columns)
        print(tabulate(df, headers = columns, tablefmt='pretty', showindex = 'never'))

        connection.commit()

        while proceed not in ["y", "n"]:
            proceed = input("Continue (y/n): ")

        match proceed:
            case "y": menu()
            case "n": exit()


def enter_books():
    
    print("============================")

    cursor.execute('''
        select ID from books;
    ''')
    rows = cursor.fetchall()

    try:
        x = rows[len(rows) - 1][0]
    except IndexError:
        x = 100

    book_name=input("Enter Book name: ")
    author_name = input("Enter author name: ")

    pub_date = input("Enter publishing date in the format yyyymmdd: ")
    while not date_format(pub_date):
        pub_date = input("Enter publishing date in the format yyyymmdd: ")
    pub_date = date_format(pub_date)        

    copies = int(input("Enter number of copies available: "))

    cursor.execute(f'''
        insert into books (ID, BOOK_NAME, AUTHOR_NAME, PUBLISHING_DATE, NUMBER_OF_COPIES_AVAILABLE) values 
        ({x+1},"{book_name}","{author_name}","{pub_date}",{copies});
    ''')

    print("Book added successfully.")
    time.sleep(2)

    connection.commit()

    menu()