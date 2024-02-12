#!/usr/bin/env python3
import serial
import time

port = '/dev/cu.usbserial-1410'
last_prb = ''
last_prb_coord = [0, 0, 0]
last_mpos = [0, 0, 0]
last_status = ''
ser = None

def read_line():
    line = ser.readline().decode().strip()
    #print('<', line)
    return line

def wait_grbl():
    while True:
        line = read_line()
        if line.startswith('Grbl '):
            return

def wait_ok():
    while True:
        line = read_line()
        if line == 'ok':
            return

def send_line(line):
    #print('>', line)
    ser.write(line.encode() + b'\r\n')
    wait_ok()

def read_status():
    global last_status

    ser.write(b'?')
    while True:
        line = read_line()
        if line.startswith('<'):
            break
    last_status = line
    return line

def read_mpos():
    global last_mpos

    status = read_status()
    mpos = list(filter(lambda x: x.startswith('MPos:'), status.split('|')))
    last_mpos = list(map(float, mpos[0].split(':')[1].split(',')))

    return last_mpos

def wait_prb():
    global last_prb, last_prb_coord

    while True:
        line = read_line()
        if line.startswith('[PRB:'):
            last_prb = line
            #print(last_prb)
            last_prb_coord = list(map(float, last_prb.split(':')[1].split(',')))
            read_status()
            return True
        if line.startswith('ALARM:'):
            send_line('$X')
            return False

def send_prb(line):
    send_line(line)
    return wait_prb()

def wait_no_prb(sleep_time=0.01):
    #print('wait_no_prb')
    while True:
        line = read_status()
        if 'Pn:P' in line:
            time.sleep(sleep_time)
        else:
            return True

def find_edge(probe_depth=-2.0, probe_axis='Z', step=2, step_axis='X', attempts=5, probe_feed=100):
    send_line('G91')
    for i in range(attempts):
        if send_prb(f'G38.2 {probe_axis}{probe_depth} F{probe_feed}'):
            send_line(f'G0 {probe_axis}{-probe_depth / abs(probe_depth)}')
            wait_no_prb()
            send_line(f'G0 {step_axis}{step}')
        else:
            if send_prb(f'G38.2 {step_axis}{-step} F{probe_feed}'):
                send_line(f'G0 {step_axis}{step/abs(step)}')
                wait_no_prb()
                send_line(f'G0 {probe_axis}{-probe_depth}')
                return True
            else:
                send_line(f'G0 {step_axis}{step}')
                return False

    return False

def find_right_edge():
    print('find_right_edge')
    return find_edge(probe_depth=-2, probe_axis='Z', step=2, step_axis='X')

def find_top_edge():
    print('find_top_edge')
    return find_edge(probe_depth=-2, probe_axis='X', step=2, step_axis='Z')

def find_back_edge():
    print('find_back_edge')
    return find_edge(probe_depth=-8, probe_axis='Z', step=10, step_axis='Y', attempts=12)

def find_face_edge():
    print('find_face_edge')
    return find_edge(probe_depth=-8, probe_axis='Z', step=-10, step_axis='Y', attempts=12)

ser = serial.Serial(port, 115200)

wait_grbl()

if True:
    if not find_right_edge():
        print("unable to find right edge")
        exit(1)

    x_right = last_prb_coord[0]

    if not find_top_edge():
        print("unable to find top edge")
        exit(1)

    z_top = last_prb_coord[2]
    z_0 = z_top - 1

    if send_prb('G91 G38.2 X-3 F100'):
        print("one more right edge found")
        exit(1)

    y_start = read_mpos()[1]

    if not find_face_edge():
        print("unable to find face edge")
        exit(1)

    y_face = last_prb_coord[1]
    if send_prb(f'G90 G38.2 Y{y_start} F1000'):
        print(f"unable to return to Y{y_start}")
        exit(1)

    if not find_back_edge():
        print("unable to find back edge")
        exit(1)

    y_back = last_prb_coord[1]
    y_0 = y_face + (y_back - y_face) / 2

    send_line(f'G90 G0 Y{y_0} X{x_right + 1}')
    send_line(f'G90 G0 Z{z_top - 5}')

    send_prb('G91 G38.2 X-2 F100')
    send_line('G91 G0 X1')
else:
    z_top = 1
    z_0 = 0

    x_right = -1
    x_0 = -1

    y_face = -51.353
    y_back = 51.353
    y_start = 0
    y_0 = 0

    send_line(f'G90 G0 Z{z_top - 5}')

if not send_prb('G91 G38.2 X-2 F10'):
    print("unable to find right edge")
    exit(1)

x_0 = last_prb_coord[0]

send_line('G91 G0 X1')

if False:
    y_size = y_back - y_face
    y_step = (y_size - 10) / 9

    for i in range(0, 10):
        y = y_face + 5 + y_step * i
        send_line(f'G90 G0 Y{y}')

        send_prb('G91 G38.2 X-2 F100')
        send_line('G91 G0 X1')

        print(y - y_0, last_prb_coord[0] - x_0)

send_line(f'G90 G0 Y{y_0} X{x_0 + 1} Z{z_0}')
