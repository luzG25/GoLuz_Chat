# Goluz_chat
Encrypted TCP client-server chat


This project is an encrypted chat between 2 or more points, allowing you to send files and text messages to each other via the terminal
 
Characteristics:
- Communication using the TCP protocol
- Symmetric key encryption with key exchange with the Diffie-Helman algorithm
- Sending text messages and files
- self-updating of code on the end client
  
Requirements:
- Python 3.+
- "Cryptography" library
- Be connected to the local network (optional)

Run chat:
- Search IPv4 address of the device to run the server program
tip: use the command in the terminal 'ipconfig' windows or 'ifconfig' in linux
- Change the Server code on line 74 to your machine's IP "bind_ip = '192.168.88.10'"
- Run the code on the server
- Change the Client code in line 222 to the IP of the machine running the Server "target_host = '192.168.88.10'"
- Execute Client code

