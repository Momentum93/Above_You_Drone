import threading, socket
#import pynvcdec
import cv2

class VideoStream():
    _debug = False
    _socket = None

    _bound_function = None

    def __init__(self,cmd ,debug = False) -> None:
        _debug = debug

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.bind(('', 11111))
            
            cmd('streamon')
        except Exception as e:
            if self._debug: print(e)
        #print("test")
        threading.Thread(target = self._handle_video_stream, daemon=True).start()

    def _handle_video_stream(self) -> None:
            #print("test")
       # while True:
            #print("foo")
            #_stream, adr = self._socket.recvfrom(2048)

            try:
                stream = cv2.VideoCapture('udp://0.0.0.0:11111')

            except Exception as e:
                if self._debug: print(e)

            try:
                while True:
                    r,f = stream.read()

                    if self._bound_function:
                        self._bound_function(r,f)
                    elif self._debug:
                        print(r,f)
            except Exception as e:
                if self._debug: print(e)

    def bind_function(self, foo) -> None:
        self._bound_function = foo
