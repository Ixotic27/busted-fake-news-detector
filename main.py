while True:
    print("1 -> Enter keywords")
    print("2 -> Enter link")
    print("3 -> Exit!")
    
    ch = int(input("Enter your choice: "))
    try: 
        if(ch==1):
           query=input("Enter the keywords: ")
        elif(ch==2):
           query=input("Enter the link: ")
        elif(ch==3):
           print("Exiting...")
           break
        else:
           print("Invalid choice! Please enter 1, 2, or 3.")
    except ValueError as e:
       print(f"Error: {e}")