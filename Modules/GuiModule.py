from tkinter import Tk
from abc import ABC, abstractmethod
import time, threading

class GUI(ABC): 
    
    _bound_function = None
    _debug = False

    def __init__(self, debug=False) -> None:
        self._debug = debug

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def run() -> None:
        pass

    def bind_update_function(self, foo) -> None:
        self._bound_function = foo



class TkGui(GUI, Tk):
    
    def __init__(self, debug=False) -> None:
        GUI.__init__(self, debug)
        Tk.__init__(self)

    def run(self) -> None:
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while True:
            if self._bound_function:
                self._bound_function()
            self.update_idletasks()
            self.update()
            time.sleep(0.01)