import socket
from threading import Thread
import time


# ******************************************************************************
# Settings
# ******************************************************************************
SRV_IP = '0.0.0.0'
SRV_PORT = 1415
BUFF_SIZE = 1024
LBR_IP = "10.84.57.105"

ai_state = 0
ai_sequence = ""
ai_config = ""


# ******************************************************************************
# Common methods and functions
# ******************************************************************************
def str_to_bytes(s: str):
    """Convert string into bytes.
    :param s: String to convert.
    :return: Bytes representation of string s.
    """
    return bytes(s, 'utf-8')

def bytes_to_str(b: bytes):
    """Convert bytes into string.
    :param b: Bytes to convert.
    :return: String representation of bytes b.
    """
    return str(b, 'utf-8')

def make_xml(target="", seq="", config=""):
    """Make XML string.
    :param target: Name of target position (optional).
    :param seq: Movement seqence (optional).
    :param config: Config parameter for movements (optional).
    :return: Returns a string in required XML format.
    """
    ret = ""
    if target != "":
        ret += f"<target>{target}</target>"
    if seq != "":
        ret += f"<seq>{seq}</seq>"
    if config != "":
        ret += f"<config>{config}</config>"
    return f"<msg>{ret}</msg>"

def make_config(tSize=1.0, rSize=1.0):
    """Make config part of XML file.
    :param tSize: Step size for translatory movement in mm (optional).
    :param rSize: Step size for rotatory movement in degrees (optional).
    :return: Returns config parameters in required XML format.
    """
    return f"<tSize>{tSize}</tSize><rSize>{rSize}</rSize>"

def make_seq_s(idx:int, seq:str):
    """Make single sequence part of XML file.
    :param idx: Index of sequence.
    :param seq: Movement sequence as string (max 50 signs).
    :return: Returns single sequence in required XML format.
    """
    #return "<s{0:02}>{1}</s{0:02}>".format(idx, seq[0:50])
    return f"<s{idx:02}>{seq[0:50]}</s{idx:02}>"

def make_test_seq():
    """Make test movement sequence.
    :return: Returns test sequence in required XML format.
    """
    ret =  make_seq_s(0, "rrrrrrrrrrrrrrrrrrrrllllllllllllllllllll")
    ret += make_seq_s(1, "45c45w")
    ret += make_seq_s(2, "100r45c")
    ret += make_seq_s(3, "150r45w")
    ret += make_seq_s(4, "30u30d20u20d100l100r")
    ret += make_seq_s(5, "10r10d10l10u")
    ret += make_seq_s(6, "rrrrrrrrrrrruuuuuuuuuuullllllllllllddddddddddd")
    ret += make_seq_s(7, "")
    ret += make_seq_s(8, "")
    ret += make_seq_s(9, "")
    ret += make_seq_s(10, "")
    ret += make_seq_s(11, "")
    ret += make_seq_s(12, "")
    ret += make_seq_s(13, "")
    ret += make_seq_s(14, "")
    ret += make_seq_s(15, "")
    ret += make_seq_s(16, "")
    ret += make_seq_s(17, "")
    ret += make_seq_s(18, "")
    ret += make_seq_s(19, "")
    return ret

# ******************************************************************************
# TCP-client's thread
# ******************************************************************************
class ClientThread(Thread):
    """TCP-client's thread."""

    def __init__(self, conn, ip, port, buff_size):
        Thread.__init__(self)
        self.conn = conn
        self.ip = ip
        self.port = port
        self.buff_size = buff_size
        print("\nCONNECTED    | Client's IP: {}:{}".format(ip, port))

    def run(self):
        global ai_state
        global ai_sequence
        global ai_config
        while True:
            try:
                data = self.conn.recv(self.buff_size)
                if not data:
                    print("LBR_DISCONNECT |")
                    break
                else:
                    print("RCV_FROM_LBR | {}".format(data))
                    data = bytes_to_str(data)
                    to_send = ""
                    if data == "HotWireStarted":
                        to_send = make_xml(target="Record")
                    elif data == "OnRecord":
                        if ai_state == 0:
                            # AI thread takes photo and calculates movement path
                            ai_state = 1
                            to_send = make_xml(target="Wait")
                        elif ai_state == 1:
                            # AI still calculates the movement path
                            to_send = make_xml(target="Wait")
                        elif ai_state == 2:
                            # AI is ready with the calculation and generates motion string
                            to_send = make_xml(target="Start", seq=ai_sequence, config=ai_config)
                            ai_state = 0
                    elif data == "NoSeq":
                        to_send = make_xml(target="Start", seq=ai_sequence, config=ai_config)
                    elif data == "Finished":
                        to_send = make_xml(target="End")
                    else:
                        to_send = ""
                    
                    if to_send != "":
                        self.conn.send(str_to_bytes(to_send))
                        print("SENT_TO_LBR  | {}".format(to_send))
            except IOError as err:
                print("IO error: {0}".format(err))
                break
        print("DISCONNECTED | Client's IP: {}:{}".format(self.ip, self.port))


# ******************************************************************************
# Test AI class and thread
# ******************************************************************************
class AiTestClass():
    def __init__(self):
        self.seq = ""
        self.config = ""

    def take_photo(self):
        photo = str(b"\xF0\x9F\x93\xB8", 'utf-8')
        print(f"\nAI take the {photo}.\n")
        time.sleep(5)
    
    def solver(self):
        pizza = str(b"\xF0\x9F\x8D\x95", 'utf-8')
        beer = str(b"\xF0\x9F\x8D\xBA", 'utf-8')
        print(f"\nAI solver is running. It's {pizza} and {beer} time! :)\n")
        time.sleep(15)
        self.seq = make_test_seq()
        self.config = make_config(1.3, 2)


class AiThread(Thread):
    def __init__(self, ai):
        Thread.__init__(self)
        self.ai = ai

    def run(self):
        global ai_state
        global ai_sequence
        global ai_config
        ai_sequence = ""
        ai_config = ""
        while True:
            if ai_state == 1:
                self.ai.take_photo()
                self.ai.solver()
                ai_sequence = self.ai.seq
                ai_config = self.ai.config
                ai_state = 2


# ******************************************************************************
# Multithreaded python server: TCP-server socket program
# ******************************************************************************
def server():
    """Multithreaded python server: TCP-server socket program."""
    clients = []

    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_server.bind((SRV_IP, SRV_PORT))
        print("### SRV: started **************************************************")
        print("### SRV: waiting for connections from TCP clients on port-no: ", SRV_PORT)
        srv_run = True
    except socket.error as err:
        print("### SRV: some errors while starting:\n", err)
        srv_run = False
        exit(1)

    while srv_run:
        tcp_server.listen(1)
        (conn, (ip, port)) = tcp_server.accept()
        if ip == LBR_IP:  # only KUKA LBR4+ allowed
            new_client = ClientThread(conn, ip, port, BUFF_SIZE)
            new_client.start()
            clients.append(new_client)

    for item in clients:
        item.join()


def ai():
    ai_test = AiTestClass()
    ai_thread = AiThread(ai_test)
    ai_thread.start()


# ******************************************************************************
# Main program
# ******************************************************************************
if __name__ == '__main__':
    ai()
    server()
