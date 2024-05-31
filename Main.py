from Modules.CommandModule import Command
from Modules.StateModule import State
from Modules.InputModule import KeyboardInput as Input
from Modules.StreamModule import VideoStream as Stream
from Modules.DecodeModule import decode_h264, h264_to_label, foo
from Modules.GuiModule import TkGui

import cv2
from PIL import Image
from PIL import ImageTk
import pickle, time
import numpy as np

from tkinter import Label


window = TkGui()
lbl = Label(window)
lbl.pack()
window.run()

obj_cmd = Command()

obj_state = State()
obj_state.bind_function((lambda str_state: print(str_state)))

obj_stream = Stream(obj_cmd, True)
def foo(return_code,frame): 
    if not return_code: 
        pass
        #raise Exception('stream error')
    img = Image.fromarray(frame)
    photo = ImageTk.PhotoImage(img)

    lbl.imgtk = photo
    lbl.configure(image=photo)
obj_stream.bind_function(foo)

obj_input = KeyboardInterrupt(obj_cmd)
def foo2(key):
    match key:
        case _ : print(key)
obj_input.bind_function(foo2)


'''


root = Tk()

label = Label(root)
label.pack()



obj_cmd('streamon')

def test():
    #t = time.time()
    time.sleep(5) # kammera muss anlaufen?
    stream = cv2.VideoCapture('udp://0.0.0.0:11111')
    #print(time.time()-t)
    #if stream.isOpened(): raise Exception('Drone-Stream not reachable')
    r,f = stream.read()
    print(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)) #ev. not notwendig

    img = Image.fromarray(f)
    print("img done")
    photo = ImageTk.PhotoImage(image=img)
    print("photo done")

    label.imgtk = photo
    label.configure(image=photo)

    return
    while True: 
        try:
            r,f = stream.read()
            


            for framedata in f:
                (frame, w, h, ls) = framedata
                if frame is not None:
                    # print 'frame size %i bytes, w %i, h %i, linesize %i' % (len(frame), w, h, ls)

                    frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
                    frame = (frame.reshape((h, ls / 3, 3)))
                    frame = frame[:, :w, :]
                    print(frame)
                    #res_frame_list.append(frame)

               

        except Exception as e: pass
        

import threading
threading.Thread(target=test, daemon=True).start()
#obj_stream = Stream(obj_cmd, False)
#obj_stream.bind_function(lambda stream : h264_to_label(label, stream))
#obj_stream.bind_function(lambda s: foo(s))


root.mainloop()


'''