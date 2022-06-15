import json
import os
from itertools import cycle
import re
from tabulate import tabulate
import pyautogui
from threading import Thread


def editable_input(text):
    Thread(target=pyautogui.write, args=(text,)).start()
    modified_input = input()
    return modified_input


def xor(data):
    key = b'1a2b3c4d1'
    if isinstance(data, dict):
        data = json.dumps(data).encode('utf-8')

    encrypted = bytes([a ^ b for (a, b) in zip(data, cycle(key))])
    return encrypted


def write_json(data):
    with open('change_me.json', 'w') as f:
        data = json.dumps(data)
        f.write(data)


def read_json():
    with open('change_me.json', 'r') as file_e:
        json_object = json.load(file_e)
    return json_object


def write_bytes(data):
    if isinstance(data, dict):
        data = json.dumps(data).encode('utf-8')
    with open('data.bin', 'wb') as f:
        f.write(data)


def read_bytes():
    bytes_data = b''
    with open('data.bin', 'rb') as file:
        for byte in iter(lambda: file.read(1), b''):
            bytes_data += byte
    return bytes_data


def file_worker():
    bytes_data = read_bytes()
    xor_data = xor(bytes_data)
    json_data = json.loads(xor_data.decode('utf-8'))
    return json_data


def save_backup(data):
    with open('data_backup.json', 'w') as f:
        data = json.dumps(data)
        f.write(data)
    return


def load_backup():
    with open('data_backup.json', 'r') as file_e:
        json_object = json.load(file_e)
        xor_data = (xor(json_object))
        write_bytes(xor_data)
    return


def edit_json(state=True):
    help = ["<save> - to save changes;", "<reset> - to reset file;", "<cancel> - to cancel changes;"]
    if state:
        print("\nEntering edit mode:")
        print("We are creating editable <data.json> file for you!")
        print("Open file and make changes!")
        print("Enter operation or type <?> for help:")
        data = file_worker()
        write_json(data)
        save_backup(data)
    else:
        print("")
    input1 = input()
    if input1 == "save":
        print("\nSaving changes...")
        try:
            data = read_json()
            write_bytes(xor(data))
            os.remove("change_me.json")
        except:
            print("Incorrect data structure:")
            print("Please use <reset> or <cancel>:")
            load_backup()
            edit_json(False)
    elif input1 == "reset":
        data = file_worker()
        write_json(data)
        print("Reset done!")
        edit_json(False)
    elif input1 == "cancel":
        print("\nCancelling changes!")
        os.remove("change_me.json")
        return
    elif input1 == "?":
        for x in help:
            print(x)
        edit_json(False)
    else:
        print("\nIncorrect command!")
        edit_json(False)


def no_validate():
    run(True)


def validate(tries=1):
    trues = 0

    print("Please enter your login:")
    login = input()
    print("\nPlease enter your password:")
    password = input()

    json_object = file_worker()

    for x in json_object["auth"]:
        if x == f"{login}:{password}":
            trues += 1

    if trues != 0:
        if login == "admin":
            print("\nSuccessfully validated as admin!")
            run(True)
        else:
            print("\nSuccessfully validated!")
            run(False)
    else:
        if tries < 3:
            print(f"\nIncorrect login or password!\n{3 - tries} tries left!\n")
            tries += 1
            validate(tries)
        else:
            print("\nYou have no tries left!\n")
            return


def print_path(path):
    str1 = ""
    for x in path:
        str1 += x
        if x != "/":
            str1 += "/"
    print(str1 + "> ", end=" ")


def run(admin=False, path=["/"]):
    # fs = ""
    help = ["<?> - for help;", "<!> - for exit;", "<logout> - to logout;", "<ls> - view structure;",
            "<cd> - change directory", "<pwd> - print working directory", "<mkdir/rmdir> - add/remove folder;",
            "<mkfile/rmfile> - add/remove file;", "<vi> - edit file;", "<cat> - print file;"]
    if admin:
        help.append("<edit> - for admin edit;")
    # print("\nEnter operation or type <?> for help:")
    print_path(path)
    command = input()
    if command == "?":
        for x in help:
            print(x)
    elif command == "!":
        quit()
    elif command == "edit" and admin:
        edit_json()
    elif command == "logout":
        print("Logged out\n")
        validate()
    elif command == "ls":
        json_object = file_worker()
        table = [["Name", "Type"]]
        fn = "json_object['structure']"
        for x in path:
            fn += f"['{x}']"
        for key in eval(fn):
            row = []
            row.append(key)
            if isinstance(eval(fn)[key], dict):
                row.append("Folder")
            else:
                row.append("File")
            table.append(row)
        print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))
    elif command == "pwd":
        str1 = ""
        for x in path:
            str1 += x
            if x != "/":
                str1 += "/"
        print("Your current path is: " + str1)
    elif re.findall("^cd [Aa-zZ/.]+[0-9]*$", command):
        if command[3:] == "/":
            path.clear()
            path.append("/")
        elif command[3:] == "..":
            path.pop()
        else:
            json_object = file_worker()
            match_found = False
            fn = "json_object['structure']"
            for x in path:
                fn += f"['{x}']"
            dict1 = eval(fn)
            for key in eval(fn):
                if key == command[3:]:
                    match_found = True
            if match_found:
                if isinstance(dict1[f"{command[3:]}"], dict):
                    path.append(command[3:])
                else:
                    print("Not a folder!")
            else:
                print("Wrong directory!")
    elif re.findall("^mkdir [Aa-zZ]+[0-9]*$", command):
        json_object = file_worker()
        match_found = False
        fn = "json_object['structure']"
        for x in path:
            fn += f"['{x}']"
        dict1 = eval(fn)
        for key in eval(fn):
            if key == command[6:]:
                match_found = True
        if match_found:
            print(f"Folder with name: {command[6:]} - already exists!")
        else:
            dict1[f"{command[6:]}"] = {}
            write_bytes(xor(json_object))
    elif re.findall("^mkfile [Aa-zZ]+[0-9]*.[a-z]+$", command):
        json_object = file_worker()
        match_found = False
        fn = "json_object['structure']"
        for x in path:
            fn += f"['{x}']"
        dict1 = eval(fn)
        for key in eval(fn):
            if key == command[7:]:
                match_found = True
        if match_found:
            print(f"File with name: {command[7:]} - already exists!")
        else:
            dict1[f"{command[7:]}"] = ""
            write_bytes(xor(json_object))
    elif re.findall("^rmfile [Aa-zZ]+[0-9]*.[a-z]+$", command):
        json_object = file_worker()
        match_found = False
        fn = "json_object['structure']"
        for x in path:
            fn += f"['{x}']"
        dict1 = eval(fn)
        for key in eval(fn):
            if key == command[7:]:
                match_found = True
        if match_found:
            dict1.pop(command[7:])
            write_bytes(xor(json_object))
            print(f"File with name: {command[7:]} - successfully deleted!")
        else:
            print(f"File with name: {command[7:]} - not found!")
    elif re.findall("^rmdir [Aa-zZ]+[0-9]*$", command):
        json_object = file_worker()
        match_found = False
        fn = "json_object['structure']"
        for x in path:
            fn += f"['{x}']"
        dict1 = eval(fn)
        for key in eval(fn):
            if key == command[6:]:
                match_found = True
        if match_found:
            dict1.pop(command[6:])
            write_bytes(xor(json_object))
            print(f"Folder with name: {command[6:]} - successfully deleted!")
        else:
            print(f"Folder with name: {command[6:]} - not found!")
    elif re.findall("^vi [Aa-zZ]+[0-9]*.[a-z]+$", command):
        json_object = file_worker()
        match_found = False
        fn = "json_object['structure']"
        for x in path:
            fn += f"['{x}']"
        dict1 = eval(fn)
        for key in eval(fn):
            if key == command[3:]:
                match_found = True
        if match_found:
            if isinstance(dict1[f"{command[3:]}"], dict):
                print("Can't edit folder!")
            else:
                print(f"Editing file with name: {command[3:]}:\n")
                a = editable_input(dict1[f"{command[3:]}"])
                print("Received input:", a)
                dict1[f"{command[3:]}"] = a
                write_bytes(xor(json_object))
        else:
            print(f"File with name: {command[3:]} - not found!")
    elif re.findall("^cat [Aa-zZ]+[0-9]*.[a-z]+$", command):
        json_object = file_worker()
        match_found = False
        fn = "json_object['structure']"
        for x in path:
            fn += f"['{x}']"
        dict1 = eval(fn)
        for key in eval(fn):
            if key == command[4:]:
                match_found = True
        if match_found:
            print("File contains:\n" + dict1[f"{command[4:]}"])
        else:
            print(f"File with name: {command[3:]} - not found!")
    else:
        print("Incorrect command!")
    run(admin, path)


if __name__ == '__main__':
    # load_backup()
    # no_validate()
    validate()
