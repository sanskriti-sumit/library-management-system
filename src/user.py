import re
import os
import pandas as pd
import sqlite3
from tabulate import tabulate

connection = sqlite3.connect("databases/library.db")

cursor = connection.cursor()

def authentication():
    """
        Somehow find a way to check the username alongside asking the user for the correct username.
    """
    global username

    pattern = re.compile(r'^[a-z]+_+[a-z]+@+\d{4}$')
    username = input("Enter username: ")
    while not pattern.match(username):
        print("Incorrect username.")
        username = input("Enter correct username: ")

def menu():

    os.system("clear")

    print("""
        ========================================
        Welcome to XYZ Library Management System
        ========================================
    """)
    options = {
        1: "Borrow Books.",
        2: "Return Books.",
        3: "Display Books.",
        4: "Exit"
    }

    print("Choose from the following option: ")
    for i, j in options.items():
        print(f"{i}. {j}")

    user_choice = None
    while user_choice not in options:
        try:
            user_choice = int(input("Enter your choice: "))
        except ValueError as e:
            print("Invalid input")
            menu()
    
    match user_choice:
        case 1:
            borrow_books()
        case 2:
            return_books()
        case 3:
            display_books()
        case 4, _:
            exit()

def proceed():
    choice = ""

    while choice not in ["y", "n"]:
        choice = input("Would you like to continue or not ? (y/n): ")

    match choice:
        case "y":
            menu()    
        case "n":
            exit()

def borrow_books():
    
    book_id = ""
    quantity_borrowed = ""

    data = username.split("@")
    name_list = data[0].split("_")
    rgsn_no = int(data[1])
    name = name_list[0].capitalize() + " " + name_list[1].capitalize()
    
    while not book_id.isnumeric():
        book_id = input("Enter the book ID corresponding to the book you wish to borrow: ")
    book_id = int(book_id)
    
    cursor.execute('''
        select ID from books;
    ''')

    rows = cursor.fetchall()    
    data = [i[0] for i in rows]

    if book_id in data: pass
    else:
        print("Invalid input")
        menu()

    cursor.execute(f'''
        select "BOOK_NAME" from books where ID = "{book_id}";
    ''')

    book_name = cursor.fetchall()[0][0]
    print(f"Book to be borrowed: {book_name}")

    cursor.execute(f"""
        select "NUMBER_OF_COPIES_AVAILABLE" from books where ID = {book_id}
    """)

    number_of_copies = cursor.fetchall()[0][0]
    print(f"Number of copies available: {number_of_copies}")

    while not quantity_borrowed.isnumeric():
        quantity_borrowed = input("Enter the number of copies you'd like to borrow: ")
    quantity_borrowed = int(quantity_borrowed)

    if number_of_copies == 0:
        print(f"No available copies of the requested book: {book_name}")
        menu()    
    elif quantity_borrowed > number_of_copies:
        print(f"Number of copies requested is more than the number of copies available. Please try again.")
        menu()
    else:

        cursor.execute(f'''
        SELECT Registration_Number, Recipient_Name, Borrowed_Book_ID
        FROM borrowed_books
        WHERE Registration_Number = {rgsn_no}
        AND Recipient_Name = '{name}'
        AND Borrowed_Book_ID = {book_id};
    ''')

        result = cursor.fetchall()
        if result:

            cursor.execute(f"""
                UPDATE borrowed_books 
                SET NUMBER_OF_COPIES_BORROWED = NUMBER_OF_COPIES_BORROWED + {quantity_borrowed}
                WHERE REGISTRATION_NUMBER = {rgsn_no} AND Borrowed_Book_Id = {book_id};
            """)
        
        else:
            
            cursor.execute(f'''
                SELECT Registration_Number, Borrowed_Book_ID
                FROM borrowed_books
                WHERE Registration_Number = {rgsn_no}
                AND Borrowed_Book_ID = {book_id};
            ''')
            res = cursor.fetchall()
            try:
                if res[0][0] == rgsn_no:
                    print("Incorrect Registration Number. Another user's records with same Registration Number exists. Please try again")
                    exit()
            except Exception:
                pass
                
            cursor.execute(f'''
                INSERT INTO borrowed_books 
                VALUES('{rgsn_no}', '{name}', '{book_id}', '{book_name}', '{quantity_borrowed}');
            ''')

        cursor.execute(f"""
            UPDATE books 
            SET "NUMBER_OF_COPIES_AVAILABLE" = "{number_of_copies - quantity_borrowed}"
            WHERE ID = "{book_id}";
        """)

        print(f"Book: {book_name} successfully issued to Recipient: {name}")
        connection.commit()
            
        proceed()
        
def return_books():

    number_of_copies = ""
    user_choice = ""

    data = username.split("@")
    name_list = data[0].split("_")
    rgsn_no = int(data[1])
    name = name_list[0].capitalize() + " " + name_list[1].capitalize()

    cursor.execute(f'''
        Select 
        Registration_Number,
        Recipient_Name,
        Borrowed_Book_ID,
        Borrowed_Book_Name,
        Number_of_Copies_Borrowed from borrowed_books 
        where Registration_Number = {rgsn_no} and "Recipient_Name" = "{name}";
    ''')
    data = cursor.fetchall()
    
    if data:
        print("Your previous record is as follows:")
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data, columns = columns)
        print(tabulate(df, headers = columns, tablefmt='pretty', showindex = 'never'))
    else:
        print("You haven't borrowed any books yet. Try again later.")
        menu()

    cursor.execute(f"""
        select Borrowed_Book_Id from borrowed_books where Registration_Number = {rgsn_no};
    """)
    book_id_list = [i[0] for i in cursor.fetchall()]

    book_id = input("Enter the id of the book you'd like to return: ")

    if int(book_id) in book_id_list: pass
    else:
        print("No records of such book being borrowed. Please try again.")
        menu()

    cursor.execute(f"""
        select Borrowed_Book_Name from borrowed_books where Borrowed_Book_ID = {book_id}; 
    """)
    
    book_name = cursor.fetchall()[0][0]
    print(f"Book to be returned: {book_name}")

    while not number_of_copies.isnumeric():
        number_of_copies = input("Enter number of copies you'd like to return: ")
    number_of_copies = int(number_of_copies)

    cursor.execute(f"""
        select Number_of_Copies_Borrowed from borrowed_books where Registration_Number = {rgsn_no} and Borrowed_Book_ID = {book_id};
    """)

    d = cursor.fetchall()[0][0]

    if number_of_copies > d:
        while user_choice not in ["y", "n"]:
            user_choice = input(f"You have only borrowed {d} copies of the {book_name}. Would you like to return all of them? (y/n): ")
        if user_choice == "y":
            number_of_copies = d
        else:
            menu()

    cursor.execute(f'''
        update books set NUMBER_OF_COPIES_AVAILABLE  =  NUMBER_OF_COPIES_AVAILABLE + {number_of_copies} where  ID = {book_id};
    ''')

    cursor.execute(f"""
        update borrowed_books set Number_of_Copies_Borrowed = Number_of_Copies_Borrowed - {number_of_copies} where Borrowed_Book_Id = {book_id} and Registration_Number = {rgsn_no};
    """)

    cursor.execute('''
        Delete from borrowed_books where Number_of_Copies_Borrowed=0;
    ''')
    connection.commit()

def display_books():
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
    print(tabulate(df, headers = columns, tablefmt='pretty', showindex = 'never'), "\n\n")
    proceed()

def start():
    authentication()
    menu()