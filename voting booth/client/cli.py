import socket
import ssl,sys

def client_connect():
    name = input("Enter your name: ")
    vr_number = input("Enter your voter registration number: ")
    password = input("Enter your password: ")
    method = "login"
    auth_msg = f"{method},{name},{vr_number},{password}".encode()
    ssl_sock.sendall(auth_msg)
    response = ssl_sock.recv(1024).decode()
    returnval = [response, name]
    return returnval

def client_register():
    name = input("Enter your name: ")
    if len(name) <= 4 or len(name)>= 12:
        print("Username must be atleast 4 characters and atmost 12 characters")
        client_register()

    ssl_sock.send(name.encode())
    response = ssl_sock.recv(1024).decode()
    if response != "OK":
        print("Username exists, Please try again.")
        client_register()
    
    while True:
        password = input("Enter your password: ")
        confirmPassword = input("Renter your password: ")
        if(password != confirmPassword):
            print("Password doesnt match, please try again.")
            continue
        break
    
    
    method = "register"
    regDetails = f"{method},{name},{password}".encode()
    ssl_sock.sendall(regDetails)
   
    response = ssl_sock.recv(1024).decode()
   
    created, voter_id = response.split(",")
    if created == "OK":
        print("Registration Successfully, Please remember your Voter Id: " + voter_id +"\n")
        regOrLogin()
    else:
        print("Registration Failed, Please try again.")
        regOrLogin()
    

def regOrLogin():
    inputVal = input("Please Login or Register if you dont have an account\n1. Login\n2. Register\n3. Exit\n")
    if inputVal == "1":

        ssl_sock.sendall(inputVal.encode())
        

        while True:

            loginDetails = client_connect()
            # print(loginDetails)
            returnedresponse = loginDetails[0]
        
            if returnedresponse != "OK":
                print("Invalid name, registration number, or password. Please try again.")
                continue

            
            print(f"Welcome {loginDetails[1].capitalize()}!.")
            while True:
                print("Please enter a number (1-4)")
                print("1. Vote")
                print("2. View election results")
                print("3. My vote history")
                print("4. Signout")
                choice = input("Enter your choice: ")
                
                if choice == "1":

                    ssl_sock.sendall("1".encode())
                    response = ssl_sock.recv(1024).decode()
                    if response == "0":
                        print("\nYou have already voted.\n")
                        continue
                        
                    else:
                        # vote = True
                        while True:
                            choice = input(response)
                            if choice != "1" and choice != "2":
                                print("\nInvalid choice. Please try again.\n")
                                continue
                            else:
                                break
                        ssl_sock.sendall(choice.encode())
                        print("\n" + ssl_sock.recv(1024).decode())
                        continue

                elif choice == "2":

                    ssl_sock.sendall("2".encode())
                    response = ssl_sock.recv(1024).decode()
                    if response != "0":
                        print("\n" + response + "\n")
                    else:
                        print("\nThe result is not available yet.\n")
                        
                    continue

                elif choice == "3":
                    ssl_sock.sendall("3".encode())
                    response = ssl_sock.recv(1024).decode()
                    print("\n" + response + "\n")
                    continue
                elif choice == "4":
                    ssl_sock.sendall("4".encode())
                    print("Goodbye.")
                    regOrLogin()
                    # ssl_sock.close()
                    # exit()
                else:
                    print("Invalid choice. Please try again.\n")
        

    elif inputVal == "2":
        ssl_sock.sendall(inputVal.encode())
        client_register()
        
    elif inputVal == "3":
        ssl_sock.sendall("Exit".encode())
        ssl_sock.close()
        exit()
    else: 
        print("Invalid selection")
        regOrLogin()


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <server_domain> <server_port>")
    sys.exit(1)

server_domain = sys.argv[1]
server_port = int(sys.argv[2])

context = ssl.create_default_context()
context.load_verify_locations("server.pem")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (server_domain, server_port)
sock.connect(server_address)
ssl_sock = context.wrap_socket(sock, server_hostname='cslongproject')



try:
    print("Welcome to University Voating System\n")

    while True:
        regOrLogin()
except ConnectionResetError:
    print("Server connection closed")