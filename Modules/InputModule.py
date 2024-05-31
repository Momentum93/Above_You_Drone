
import keyboard, threading
from abc import ABC, abstractmethod


class Input(ABC): 

    _debug = False
    _bound_function = None
    _command_module = None

    def __init__(self, command_module=None, debug=False) -> None:
        super().__init__()
        
        self._debug = debug
        if command_module: self._command_module = command_module

        threading.Thread(target=self._handle_input, daemon=True).start()

    @abstractmethod
    def _handle_input(self) -> None: pass

    def bind_function(self, foo) -> None:
        #choose which function should handle the input
        self._bound_function = foo
    
class KeyboardInput(Input): 

    def _handle_input(self) -> None:
        while True:
            try:
                key = keyboard.read_key()
                if self._bound_function:
                    self._bound_function(key)
                else:
                    if self._debug: print(key)
            except Exception as e:
                if self._debug: print(e)