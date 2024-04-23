import sys

print(sys.path)
ack = 0
check = False
selection = input("what are you testing While loop or For loop or search (w/f/s): ")
if selection == "w":
    #while loop
    while ack < 15:
        ack += 1
        print(ack)
    if check == False:
        print(str("The value of check is ") , check)
        print(str("Updating variable to True"))
        check = True
    else:
        print(check)
        exit(0)
elif selection == "f":
    #for loop
    with open(".venv/list.txt","r") as list:
    #f = open(".venv/list.txt","r")
    #print(f.read())
        for line in list:
            print(list.read())
    exit()
elif selection == "s":
    # Changed variable name to avoid shadowing built-in type `list`
    names = input("List some names in CSV format: ")
    # Splitting the input CSV string into a list of names
    name_list = names.split(",")
    print(name_list)
    for name in name_list:  # Iterating through each name in the list
        print(name) #.strip())  # Printing each name after stripping any leading/trailing whitespaces
        exit()
