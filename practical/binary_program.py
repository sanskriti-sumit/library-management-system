'''
Create a binary file with name and roll number. Search for a given roll number and display the name, if not found display appropriate message.
'''
import pickle

def menu():
    available_functions = {
        1: "Add Records",
        2: "View Records",
        3: "Search Records",
        4: "Exit"
    }

    print("Available functions are: ")
    for i, j in available_functions.items():
        print(f"{i}. {j}")
    
    user_choice = None
    while user_choice not in available_functions:
        user_choice = int(input("Enter your choice: "))

    match user_choice:
        case 1:
            write()
        case 2:
            read()
        case 3:
            search_roll_no()
        case 4:
            exit()

def proceed():
    ask = input("Do you want to continue (y/n): ")
    match ask:
        case "y":
            menu()
        case "n", _:
            exit()
            
def write():
    name = input("Enter name: ")
    roll_no = int(input("Enter roll no: "))
    with open("databases/students.dat", "ab") as file:
        pickle.dump([name, roll_no], file)
    
    proceed()

def read():
    with open("databases/students.dat", "rb") as file:
        try:
            while True:
                loaded_data = pickle.load(file)
                print(loaded_data)
        except EOFError:
            pass
    
    proceed()

def search_roll_no():
    record = False
    searched_roll_no = int(input("Enter roll no: "))
    with open("databases/students.dat", "rb") as file:
        try:
            while True:
                searched_data = pickle.load(file)
                if searched_roll_no in searched_data:
                    record = True
                    break

        except EOFError: 
            pass

    if record:
        print("Name: ", searched_data[0])
    else: 
        print("Record not found. Please try again.")

    proceed()

menu()
