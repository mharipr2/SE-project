import multiprocessing
import os
import socket
import ssl
import hashlib,sys
import datetime
import random
import pymongo


mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
db = mongo_client['voting_db']

# This code is for running 1st time in any local system

existing_collections = db.list_collection_names()

if "voters" not in existing_collections and "history" not in existing_collections and "results" not in existing_collections:

    db.create_collection("voters")
    db.create_collection("history")
    db.create_collection("results")

    resultsHardData = [
    {
        "name": "Chris",
        "votes": 0,
    },
    {
        "name": "Linda",
        "votes": 0,
    }
    ]

    voters_collection = db['voters']
    history_collection = db['history']
    results_collection = db['results']

    results_collection.insert_many(resultsHardData)

else:
    voters_collection = db['voters']
    history_collection = db['history']
    results_collection = db['results']

# 1st time code ends
# print(existing_collections)
    


#const url = 'mongodb://0.0.0.0/Intern';



def process1():
        
    while True:    
        with open("symmetric.key", "rb") as f:
            symmetric_key = f.read()


        def verify_password(regno, password):

            userdata = voters_collection.find_one({"regno": int(regno)})

            if not userdata["regno"]:
                return "incorrect regno"
            encrypted_password = userdata["password"]

            hash_password = hashlib.sha256(symmetric_key + bytes(password, 'utf-8')).hexdigest()

            if(hash_password == encrypted_password):
                return True
            else:
                return "incorrect password"


        if len(sys.argv) < 2:
            print("Usage: python sftp_server.py <server_port>")
            sys.exit(1)

        try:
            server_port = int(sys.argv[1])
        except ValueError:
            print("Error: Invalid port number")
            sys.exit(1)

        if server_port < 1024 or server_port > 65535:
            print("Error: Port number must be between 1024 and 65535")
            sys.exit(1)




        #print(socket.gethostname())

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = socket.gethostname()
        server_socket.bind((hostname, server_port))
        server_socket.listen(1)
        #server_socket.settimeout(20)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile="server.pem", keyfile="server.key")

        print('Server started and listening...')

        while True:

            connection, client_address = server_socket.accept()
            print(f"Client connected from {client_address}")


            def client_register():
                        name = ssl_conn.recv(1024).decode()
                        if not voters_collection.find_one({"name": name}):
                            ssl_conn.sendall("OK".encode()) 
                        else:
                            ssl_conn.sendall("Username already exists".encode())
                            client_register()

                        message = ssl_conn.recv(1024).decode().strip()
                        method, name, password = message.split(",")
                        while True:
                            regno = random.randint(100000, 999999)
                            if voters_collection.find_one({"regno": regno}):
                                continue
                            break

                        hash_password = hashlib.sha256(symmetric_key + bytes(password, 'utf-8')).hexdigest()

                        voter_data = {
                                        "name": name,
                                        "regno": regno,
                                        "password": hash_password
                                    }

                        voters_collection.insert_one(voter_data)


                        response = "OK"
                        
                        connection = f"{response},{regno}".encode()
                        ssl_conn.sendall(connection)
            
            try:
                ssl_conn = context.wrap_socket(connection, server_side=True)

                while True:
                    data = ssl_conn.recv(1024).decode()

                    if data == '1':
                        pass
                    elif data == '2':
                        client_register()
                        continue
                        ##under coding
                    elif data == "Exit":
                        print("Client logged out")
                        break
                    else:
                        continue

                    message = ssl_conn.recv(1024).decode().strip()

                    method, name, regno, password = message.split(",")
                    currentuser = name
                    result = verify_password(regno, password)

                    if result == "incorrect regno" or result == "incorrect password":

                        text = "0"
                        print("Authentication failed.")
                        ssl_conn.sendall(text.encode())
                        continue
                    else:
                        text = "OK"
                        print("Client logged in")
                        ssl_conn.sendall(text.encode())

                    while True:

                        data = ssl_conn.recv(1024).decode()              

                        if data == "1":

                            if history_collection.find_one({"name": currentuser}):
                                ssl_conn.sendall("0".encode())
                            
                            else:
                                ssl_conn.send("\nCandidates: (enter 1 or 2)\n1. Chris\n2. Linda\n".encode())

                                candidate_choice = ssl_conn.recv(1024).decode()
                                now = datetime.datetime.now()
                                votedtime = now.strftime("%Y-%m-%d %H:%M:%S")

                                

                                
                                if candidate_choice == "1":
                                    resultdata = results_collection.find_one({"name": "Chris"})
                                    resultdata["votes"] += 1
                                    results_collection.update_one({"_id": resultdata["_id"]}, {"$set": {"votes": resultdata["votes"]}})
                                else:
                                    resultdata = results_collection.find_one({"name": "Linda"})
                                    resultdata["votes"] += 1
                                    results_collection.update_one({"_id": resultdata["_id"]}, {"$set": {"votes": resultdata["votes"]}})

                                history_data = {
                                        "name": currentuser,
                                        "regno": int(regno),
                                        "voted_datetime": votedtime
                                    }

                                history_collection.insert_one(history_data)

                                ssl_conn.send("Thank you for your vote!\n".encode())


                        elif data == "2":

                            voters = voters_collection.count_documents({})
                            totalVotesRegistered = history_collection.count_documents({})
                            
                            if voters != totalVotesRegistered:
                                ssl_conn.send("0".encode())
                            else:
                                results_collection.create_index([("votes", pymongo.DESCENDING)])
                                highest_votes_document = results_collection.find_one({}, sort=[("votes", pymongo.DESCENDING)])
                                message = "Won: " + highest_votes_document["name"] + "\n"
                                ssl_conn.send(message.encode())


                        elif data == "3":

                            if not history_collection.find_one({"name": currentuser}):
                                yourhistory = "You have not voted yet."
                            else:
                                historyData = history_collection.find_one({"name": currentuser})
                                yourhistory = "You have already voted at " + historyData["voted_datetime"]

                            ssl_conn.send(yourhistory.encode())
            
                        elif data == "4":
                            print("Client logged out")
                            break
                            
                        else:
                            ssl_conn.send("Invalid Request.")

                    
            

                



            except ssl.SSLError as e:
                print(f'SSL error: {e}')
                server_socket.close()
                ssl_conn.shutdown(socket.SHUT_RDWR)
                ssl_conn.close()
                mongo_client.close()
            except socket.error as e:
                print(f'Socket error: {e}')
                server_socket.close()
                ssl_conn.shutdown(socket.SHUT_RDWR)
                ssl_conn.close()
                mongo_client.close()




def process2(queue):
    while True:
        if not queue.empty() and queue.get() == "stop":
            break



if __name__ == '__main__':

    queue = multiprocessing.Queue()


    process_one = multiprocessing.Process(target=process1)
    process_two = multiprocessing.Process(target=process2, args=(queue,))

    process_one.start()
    process_two.start()

    while True:
        user_input = input("Enter 'shutdown' to stop the server. ")
        if user_input.lower() == "shutdown":
            process_one.terminate()
            queue.put("stop")
            break
        else:
            print("Invalid server side command. Please use shutdown command to stop the server.")


    process_one.join()
    process_two.join()

