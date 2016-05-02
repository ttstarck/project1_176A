import socket               # Import socket module                              
import sys


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = sys.argv[1]
port = int(sys.argv[2])

s.connect((host,port))
# Hello
s.sendall('HELLO\n\n')
helloData = s.recv(1024)
print(helloData)
sessionID = helloData[24:]
sessionID = sessionID[:32]
#print(sessionID)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = sys.argv[1]
port = int(sys.argv[2])

s.connect((host,port))
s.sendall('ADD_USER ' + sessionID + ', TStarckDWang, ttstarck@umail.ucsb.edu, 7885650\n\n')
addUserData = s.recv(1024)
print(addUserData)


for i in range(0,3):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = sys.argv[1]
        port = int(sys.argv[2])
        s.connect((host,port))
        
	s.sendall('ASK ' + sessionID +'\n\n')
	askData = s.recv(1024)
        print(askData)
        askData = askData.split()
	questionID = askData[1]
	questionType = askData[2]
	num1 = int(askData[3])
	num2 = int(askData[4])
	
	result = 0
	if (questionType == "SUM"):
		result = num1 + num2
	else:
		result = num1 * num2
	result = str(result)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = sys.argv[1]
        port = int(sys.argv[2])
        s.connect((host,port))
        
	s.sendall('ANSWER ' + questionID + ' ' + result + '\n\n')
	answerData = s.recv(1024)
        print(answerData)
	answerData = answerData[:2]
	while(answerData == 'FA'):
                 s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                 host = sys.argv[1]
                 port = int(sys.argv[2])
                 s.connect((host,port))
                 
		 s.sendall('ANSWER ' + questionID + ' ' + result + '\n\n')
		 answerData = s.recv(1024)
                 print(answerData)
		 answerData = answerData[:2]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = sys.argv[1]
port = int(sys.argv[2])
s.connect((host,port))
s.sendall('SCORE ' + sessionID + '\n\n')
scoreData = s.recv(1024)
print(scoreData)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = sys.argv[1]
port = int(sys.argv[2])
s.connect((host,port))
s.sendall('BYE ' + sessionID + '\n\n')
goodbye = s.recv(1024)
print(goodbye)


s.close

