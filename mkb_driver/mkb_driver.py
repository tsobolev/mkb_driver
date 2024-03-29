#!./venv/bin/python

import sys
import json
import struct
import logging
import subprocess
from hc import HumanizeMouseTrajectory
import time

driver_version = "0.1"
msleep = lambda x: time.sleep(x/1000.0)


logging.basicConfig(filename='/tmp/mkb_driver_debug.log', encoding='utf-8', level=logging.DEBUG)
logging.debug('mkb_driver start')
allowed_keycodes = set()
allowed_keycodes.update(range(2,12)) #numbers
allowed_keycodes.update(range(12,14))
allowed_keycodes.update(range(16,28))
allowed_keycodes.update(range(30,42))
allowed_keycodes.update(range(44,54))
allowed_keycodes.add(57)

logging.debug(allowed_keycodes)
exception_msg = {"error":"something went wrong"}

def abs2rel(absolute_curve):
    relative_curve = []
    cululative = [0,0]
    fraction = [0.,0.]
    for i in range(len(absolute_curve)):
        if i == 0:
            pass
        else:
            x_float = (absolute_curve[i][0] - cululative[0]) + fraction[0]
            y_float = (absolute_curve[i][1] - cululative[1]) + fraction[1]
            fraction[0] = x_float - int(x_float)
            fraction[1] = y_float - int(y_float)
            x = int(x_float)
            y = int(y_float)
            cululative[0] += x
            cululative[1] += y
            relative_curve.append((x,y))
    return relative_curve

def getMessage():
    rawLength = sys.stdin.buffer.read(4)
    if len(rawLength) == 0:
        logging.debug('exit 0')
        sys.exit(0)
    messageLength = struct.unpack('@I', rawLength)[0]
    message = sys.stdin.buffer.read(messageLength).decode('utf-8')
    jsonMessage = json.loads(message)
    try:
        jsonMessage = json.loads(jsonMessage)
        return jsonMessage
    except:
        return {'string':jsonMessage}

def encodeMessage(messageContent):
    encodedContent = json.dumps(messageContent, separators=(',', ':')).encode('utf-8')
    encodedLength = struct.pack('@I', len(encodedContent))
    return {'length': encodedLength, 'content': encodedContent}

def sendMessage(encodedMessage):
    sys.stdout.buffer.write(encodedMessage['length'])
    sys.stdout.buffer.write(encodedMessage['content'])
    sys.stdout.buffer.flush()

def ans(msg):
    sendMessage(encodeMessage(msg))

def mousemove(msg):
    try:
        x = int(msg['x'])
        y = int(msg['y'])
        cmd = ['ydotool','mousemove','-x',str(x),'-y',str(y)]
        logging.debug(cmd)
        subprocess.run(cmd)
        return {"result":"ok"}
    except:
        return {"error":"something went wrong"}

def mousewheel(msg):
    try:
        x = int(msg['x'])
        y = int(msg['y'])
        cmd = ['ydotool','mousemove','-w','--',str(x),str(y)]
        logging.debug(cmd)
        subprocess.run(cmd)
        return {"result":"ok"}
    except:
        return {"error":"something went wrong"}
def enter(msg):
    try:
        cmd = ['ydotool','key','28:1','28:0']
        logging.debug(cmd)
        subprocess.run(cmd)
        return {"result":"ok"}
    except:
        return exception_msg
def sequence(msg):
    try:
        keycodes = msg['keycodes']
        press = msg['press']
        delay = msg['delay']
        shift = msg['shift']
        command = ''
        keys = []
        for i in range(len(keycodes)):
            c = int(keycodes[i])
            if c in allowed_keycodes:
                keys.append(c)
                p = min(int(press[i]) - 1,20)
                d = min(int(delay[i]) - 1,20)
                if shift[i] == 0:
                    command += " " + str(c) + ":1" + ' n'*p + " " + str(c) + ":0" + ' n'*d 
                else:
                    command += " 42:1 " + str(c) + ":1" + ' n'*p + " " + str(c) + ":0 42:0" + ' n'*d 
        cmd = ['ydotool','key'] + command.split(' ')[1:]
        logging.debug(cmd)
        subprocess.run(cmd)
        return {"result":"ok","keys":keys}
    except:
        return exception_msg

def switch_keymap(msg):
    try:
        cmd = ['ydotool','key','125:1','d','d','57:1','d','d','57:0','d','d','125:0','d','d']
        logging.debug(cmd)
        subprocess.run(cmd)
        return {"result":"ok"}
    except:
        return exception_msg
def bs(msg):
    try:
        count = msg['count']
        cmd = ['ydotool','key']
        keys = ['14:1','14:0']
        cmd = cmd + keys * int(count)
        logging.debug(cmd)
        subprocess.run(cmd)
        return {"result":"ok"}
    except:
        return exception_msg
def click(msg):
    try:
        count = msg['count']
        cmd = ['ydotool','click','-r',str(count),'40','80']
        logging.debug(cmd)
        subprocess.run(cmd,stdout=subprocess.DEVNULL)
        return {"result":"click ok"}
    except:
        return exception_msg

def traj(msg):
    try:
        logging.debug('traj')
        from_point = msg['from_point']
        to_point = msg['to_point']
        logging.debug(from_point)
        logging.debug(to_point)
        human_curve = HumanizeMouseTrajectory(from_point,to_point)
        return {"reuslt":"ok","traj":human_curve.points}
    except:
        return exception_msg
def mousemovetraj(msg):
    try:
        logging.debug('mousemovetraj')
        from_point = [0,0]
        to_point = msg['to_point']
        human_curve = HumanizeMouseTrajectory(from_point,to_point)
        rel_curve = abs2rel(human_curve.points)
        for point in rel_curve:
            cmd = ['ydotool','mousemove','-x',str(point[0]),'-y',str(point[1])]
            subprocess.run(cmd,stdout=subprocess.DEVNULL)
            msleep(3)
        return {"reuslt":"ok","traj":rel_curve}
    except:
        return exception_msg
def version(msg):
    return {"result":"ok","version":driver_version}

while True:
    receivedMessage = getMessage()
    logging.debug('receivedMessage:' + json.dumps(receivedMessage))
    if "action" in receivedMessage.keys():
        match receivedMessage['action']:
            case "mousemove":
                ans(mousemove(receivedMessage))
            case "mousewheel":
                ans(mousewheel(receivedMessage))
            case "enter":
                ans(enter(receivedMessage))
            case "sequence":
                ans(sequence(receivedMessage))
            case "click":
                ans(click(receivedMessage))
            case "bs":
                ans(bs(receivedMessage))
            case "switch_keymap":
                ans(switch_keymap(receivedMessage))
            case "traj":
                ans(traj(receivedMessage))
            case "mousemovetraj":
                ans(mousemovetraj(receivedMessage))
            case "version":
                ans(version(receivedMessage))
            case _:
                ans({"error":"wrong command"})
    else:
        sendMessage(encodeMessage({"error":"wrong format"}))


