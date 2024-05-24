import socket, threading

class State():

    _state_port = 8890
    _debug = False

    _bound_function = None

    def __init__(self, debug=False) -> None:
        self._debug = debug

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(('', self._state_port))

            threading.Thread(target = self._handle_incomming_state, daemon=True).start()

        except Exception as e: 
            if self._debug: print(e)

    def _handle_incomming_state(self) -> None:
        while True:
            try:
                
                _state = self.socket.recvfrom(1024)
                if self._bound_function:
                    
                    self._bound_function(_state)
                else:
                    if self._debug: print(_state)
                    else:
                        pass
            except Exception as e:
                if self._debug: print(e)

    def bind_function(self,foo) -> None:
        #choose which function should handle the incomming state
        self._bound_function = foo
