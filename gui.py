import tkinter
import socket
import threading
import time

import keyboard

from PIL import Image
from PIL import ImageTk

import numpy as np

#import libh264decoder



#ToDo: Warnmeldung wenn sich wlan ändert - z.B.: wenn drohne inaktiv geht

class Window(tkinter.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.x = 0
        self.y = 0
        self.z = 0
        self.speed = 10

        #self.decoder = libh264decoder.H264Decoder()

        self.state_strVar = tkinter.StringVar(self, "")
        self.state_label = tkinter.Label(self, textvariable=self.state_strVar)
        self.state_label.pack()

        self.response_strVar = tkinter.StringVar(self, "")
        self.response_Label = tkinter.Label(self, textvariable=self.response_strVar)
        self.response_Label.pack()

        self.video_label  = tkinter.Label(self)
        self.video_label.pack()

        

        self.connect()
        self.activate()

        self.handle_input()

        self.listen_for_response()
        self.lisen_for_state()
        #self.listen_for_video_stream()

        #self.send_command('battery?')

        self.mainloop()

    def handle_input(self) -> None:
        self.input_threat = threading.Thread(target=self._handle_input)
        self.input_threat.daemon = True
        self.input_threat.start()

    def connect(self) -> None:
        self.drone_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.drone_socket.bind(('', 8889))

    def send_command(self, cmd) -> None:
        if self.drone_socket:
            self.drone_socket.sendto(cmd.encode('utf-8'), ('192.168.10.1', 8889))
        else: pass #ToDo error Handling

    def activate(self) -> None:
        self.send_command('command')
        self.send_command('streamon')

    def listen_for_response(self) -> None:
        self.response_threat = threading.Thread(target = self._handle_response)
        self.response_threat.daemon = True
        self.response_threat.start()

    def lisen_for_state(self) -> None:
        self.state_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.state_socket.bind(('', 8890))
        self.state_thread = threading.Thread(target = self._handle_state)
        self.state_thread.daemon = True
        self.state_thread.start()

    def listen_for_video_stream(self) -> None:
        self.stream_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.stream_socket.bind(('', 11111))
        self.stream_thread = threading.Thread(target = self._handle_video_Stream)
        self.stream_thread.daemon = True
        self.stream_thread.start()

    def _handle_response(self):
        while True:
            #print('foo')
            str_response = self.drone_socket.recvfrom(1024)
            ##print(str_response)
            self.response_strVar.set(str(str_response))

    def _handle_state(self) -> None:
        while True:
            str_state = self.state_socket.recvfrom(1024)
            self.state_strVar.set(str(str_state))

    def _handle_video_Stream(self) -> None: 
        while True:
            print('test')
            #ToDo limit fps?
            tmp,adr = self.stream_socket.recvfrom(2048)
            #ToDo: implement image pooling -> see example on github from tello api

            tmp = self._h264_decode(tmp)
            #if tmp: print(type(tmp))
            img = Image.fromarray(tmp)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
    '''
    def _h264_decode(self, packet_data):
        #from tello api
        """
        decode raw h264 format data from Tello
        
        :param packet_data: raw h264 data array
       
        :return: a list of decoded frame
        """
        res_frame_list = []
        frames = self.decoder.decode(packet_data)
        for framedata in frames:
            (frame, w, h, ls) = framedata
            if frame is not None:
                # print 'frame size %i bytes, w %i, h %i, linesize %i' % (len(frame), w, h, ls)

                frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
                frame = (frame.reshape((h, ls / 3, 3)))
                frame = frame[:, :w, :]
                res_frame_list.append(frame)
    '''
    def _handle_input(self) -> None:

        #ToDo: send Idle command - cause of auto turn off
        while True:
            match pattern := keyboard.read_key():
                case '1' : self.send_command('takeoff') ;time.sleep(1) # is it harmfull if "takeoff" is spamed?

                case '2' : self.send_command('land')

                #x y z speed[cm/sec]
                case 'w' : print('w'); self.send_command('go 20 0 0 20'); print('w')
                #ToDo: up/down etc

                case 'a' : self.send_command('ccw 10')
                case 'd' : self.send_command('cw 10')

                case 'r' : self.send_command('stop')

                case _ : print(pattern)
            

window = Window()