import socket
import hashlib
import struct
import threading

def send_message(s): #function to send instructions to the server
    while (remaining_time>0):
        message_type = input("Enter Your Instruction Type: \n") #to get and classify instruction type
        if message_type == "00": #start game
            sender = struct.pack('B', 0)
            s.sendall(sender)
            game_started_message = s.recv(1024)
            print(game_started_message)
        if message_type == "01": #terminate the game
            sender = struct.pack('B', 1) 
            s.sendall(sender)
        if message_type == "02": #fetch the next question
            sender = struct.pack('B', 2)
            s.sendall(sender)
        if message_type == "03": #buy a letter
            sender = struct.pack('B', 3)
            s.sendall(sender)
        if message_type == "04": #take a guess
            guessed_word = input('Enter Your Guess: \n').encode()
            instruction = struct.pack('B', 4)
            sender = instruction + guessed_word #sent both instruction type and guessed word
            s.sendall(sender)
        if message_type == "05": #get remaining time
            sender = struct.pack('B', 5)
            s.sendall(sender)

def recieve_message(s):
    while(True):
        recieved_message = s.recv(1024)
        packet_type = struct.unpack('B',recieved_message[0:1])[0] #to classify by packet type

        if packet_type == 0: #information
            encoding_type = struct.unpack('b',recieved_message[1:2])[0]
            size = struct.unpack('<h',recieved_message[2:4])[0]
            if encoding_type == 0:
                information_message = recieved_message[4:4+size].decode('utf-8')
            if encoding_type == 1:
                information_message = recieved_message[4:4+(size*2)].decode('utf-16')
            print(information_message)
        
        if packet_type == 1: #question
            encoding_type = struct.unpack('b',recieved_message[1:2])[0]
            size = struct.unpack('<h',recieved_message[2:4])[0]
            word_lenght = struct.unpack('<h',recieved_message[4:6])[0]
            if encoding_type == 0:
                question = recieved_message[6:6+size].decode('utf-8')
            if encoding_type == 1:
                question = recieved_message[6:6+(size*2)].decode('utf-16')
            print("Word Len: ", word_lenght)
            print("Question: ",question)
        
        if packet_type == 2: #letter from the word
            pos_of_letter = struct.unpack('b', recieved_message[2:3])[0]
            letter = recieved_message[3:4].decode('utf-8')
            print("Position of Letter: ", pos_of_letter)
            print("Letter: ", letter)
        
        if packet_type == 3: #remaining time
            N_A = struct.unpack('b', recieved_message[2:3])[0]
            remaining_time = struct.unpack('<h', recieved_message[4:6])[0]
            print("Remaining Time: ", remaining_time)
        
        if packet_type == 4: #end of game
            score = struct.unpack('<h', recieved_message[2:4])[0]
            remaining_time = struct.unpack('<h', recieved_message[4:6])[0]
            print("Score: ", score)
            print("Remaining Time: ", remaining_time)
            break

HOST = "160.75.154.126"
PORT = 2022
remaining_time = 300

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"Start_Connection")
        randomHex = s.recv(1024).decode("utf-8")
        hexKey = "hexKey"
        string = randomHex + hexKey
        sha1result = hashlib.sha1(string.encode())
        authentication = sha1result.hexdigest() + "#150200039"
        s.send(authentication.encode())
        authentication_confirmation = s.recv(1024).decode("utf-8")
        print(authentication_confirmation)
        s.sendall("Y".encode())
        
        #different threads for asynchronous communication
        t1 = threading.Thread(target=recieve_message, args=(s,))
        t2 = threading.Thread(target=send_message, args=(s,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()