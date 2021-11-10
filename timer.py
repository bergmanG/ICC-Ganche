import time

global_timer = {'start': 0, 'cumTime': 0}


def start():
    global_timer['start'] = time.time()


def stop():
    global_timer['cumTime'] += time.time()-global_timer['start']


def reset():
    stop()
    temp = global_timer['cumTime']
    global_timer['cumTime'] = 0
    return temp
