import socket, threading, time

#Generall stuff:
#initial 'command' not needed -> see: _handling_command_queue()

class Command(): 
    socket = None

    _drone_ip   = '192.168.10.1'
    _drone_port = 8889

    _debug = None

    _command_queue = []

    _previous_cmd = None
    _response = None

    def __init__(self, debug=False) -> None:
        #@param 
        # - debug: Bool, is debug mode,
        #initialize: 
        # - socket for base drone communication
        # - thread for command acknowledge

        self._debug = debug

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(('', self._drone_port))

            threading.Thread(target = self._recieve, daemon=True).start()
            threading.Thread(target = self._handling_command_queue, daemon=True).start()

        except Exception as e: 
            if self._debug: print(str(e) + 'foo')

    def __call__(self, cmd) -> None:
        #adding commands to the command queue
        self._command_queue.append(cmd)

    def _handling_command_queue(self) -> None:
        #Sending the commands

        #init python mode on drone
        #generates ('hopefully') also first acknowledge msg
        self.socket.sendto('command'.encode('utf-8'), (self._drone_ip, self._drone_port))
        _time = time.time()

        while True:
            try:

                #preventing auto-turn-off (is >=15 sec):
                if self._command_queue == [] and time.time() - _time >= 10:
                    self.socket.sendto('command'.encode('utf-8'), (self._drone_ip, self._drone_port))
                    _time = time.time()

                #only sending new command if previous has acknowledge:
                if self._response:

                    if self._debug: 
                        print(f'({self._previous_cmd},{self._response})')

                    cmd = self._command_queue.pop(0)
                    self._previous_cmd = cmd

                    #if list is empty 'IndexError' is raised...
                    #-> will skip socket.sendto(...)
                    self.socket.sendto(cmd.encode('utf-8'), (self._drone_ip, self._drone_port))

                    #clearing previous _response:
                    self._response = None

                    #when was last command...
                    _time = time.time()

            except Exception as e: 
                if self._debug: print(e)

    def _recieve(self) -> None:
        #recieving the _response for sent commands
        try:
            self._response, _adr = self.socket.recvfrom(1024)
            self._response = str(self._response)

            if self._debug: print(self._response)
        except Exception as e: 
            if self._debug: print(e)






