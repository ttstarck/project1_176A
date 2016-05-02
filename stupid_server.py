# stupid server

import logging
import sys
import threading
import SocketServer
# note: to run this, you will have to pip install sqlitedict inside your virtual environment
from sqlitedict import SqliteDict
from uuid import uuid4
import random

HOST = '127.0.0.1'
PORT = 22000

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

def get_db():
    """
    Returns an sqlite-backed dict object.
    Having each thread call this provides a unique connection. Without shared connections, we should be safe.
    This is a bit sloppy. By not using a context manager, we should explicity call dict.close() when we are done.
    """
    return SqliteDict('./proj1.sqlite', autocommit=True)


class StupidServerHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            print "handling"
            data = self.request.recv(1024)
            while data[-2:] != "\n\n":
                data += self.request.recv(1024)
            logger.info(data)
            command = data.split(" ")[0].strip()
            responders = {
                "HELLO": self.hello,
                "ADD_USER": self.add_user,
                "SCORE": self.score,
                "ASK": self.ask,
                "ANSWER": self.answer,
                "BYE": self.bye,
                }
            responders[command](data)
            data = ""
        except Exception as e:
            logger.exception(e)
            self.request.send("ERROR {}\n\n".format(e))

    def hello(self, data):
        """
        Creates a session for users.
        """
        session_id = uuid4().hex
        db = get_db()
        db[session_id] = {'error_response': random.randint(0,2), 'current': 0, 'users': [], 'scores': ["NONE", "NONE", "NONE"], 'said_goodbye': False}
        db.close()
        response = "HELLO. YOUR SESSION IS: {session_id}\n\n".format(session_id=session_id)
        self.request.send(response)

    def add_user(self, data):
        """
        Adds a user to a session.
        """
        # parse the add_user line
        session_id, username, email, perm = map(lambda x: x.strip(), " ".join(data.split(" ")[1:]).split(","))
        db = get_db()
        session_data = db[session_id]
        session_data['users'].append({'username':username, 'email':email, 'perm':perm})
        db[session_id] = session_data
        db.close()
        response = "ADDED {perm}\n\n".format(perm=perm)
        self.request.send(response)

    def score(self, data):
        """
        Returns the score response.
        """
        session_id = data.split(" ")[1].strip()
        db = get_db()
        session_data = db[session_id]
        db.close()
        user_lines = "\n".join(map(lambda x: "USER: {perm}".format(perm=x['perm']), session_data['users']))
        scores = session_data['scores']
        response = """SCORE: {session_id}
{user_lines}
QUESTION 1: {score1}
QUESTION 2: {score2}
QUESTION 3: {score3}

""".format(session_id=session_id,user_lines=user_lines,score1=scores[0],score2=scores[1],score3=scores[2])
        self.request.send(response)

    def ask(self, data):
        """
        Asks a simple arithmetic problem.
        """
        session_id = data.split(" ")[1].strip()
        db = get_db()
        session_data = db[session_id]
        sum_or_mult = "SUM" if random.randint(0,1)==0 else "MULT"
        num1 = random.randint(1,99)
        num2 = random.randint(1,99)
        answer = num1*num2 if sum_or_mult == "MULT" else num1+num2
        id = uuid4().hex
        db[id] = {'belongs_to_session_id':session_id, 'answer': answer}
        db.close()
        response = "QUESTION {id} {sum_or_mult} {num1} {num2}\n\n".format(id=id, sum_or_mult=sum_or_mult, num1=num1, num2=num2)
        self.request.send(response)

    def answer(self, data):
        """
        Processes an answer or returns a fake error (once).
        """
        id = data.split(" ")[1].strip()
        user_answer = data.split(" ")[2].strip()
        db = get_db()
        question_data = db[id]
        session_data = db[question_data['belongs_to_session_id']]
        response = None
        if session_data['error_response'] == session_data['current']:
            response = "FAKEERROR - Your answer was not accepted, resubmit\n\n"
            session_data['error_response'] = -1
        else:
            if str(question_data['answer']) == str(user_answer):
                session_data['scores'][session_data['current']] = "OK"
                session_data['current'] = session_data['current'] + 1
            else:
                session_data['scores'][session_data['current']] = "FAIL"
            response = "OK - Your answer was accepted\n\n"
        db[question_data['belongs_to_session_id']] = session_data
        db.close()
        self.request.send(response)

    def bye(self, data):
        """
        Marks a session as complete for grading.
        """
        session_id = data.split(" ")[1].strip()
        db = get_db()
        session_data = db[session_id]
        session_data['said_goodbye'] = True
        db[session_id] = session_data
        db.close()
        response = "GOODBYE\n\n"
        self.request.send(response)

class ThreadedStupidServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    # Ctrl-C will cleanly kill all spawned threads
    daemon_threads = True
    # much faster rebinding
    allow_reuse_address = True

if __name__ == '__main__':
    server = ThreadedStupidServer((HOST, PORT), StupidServerHandler)
    # terminate with Ctrl-C
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)