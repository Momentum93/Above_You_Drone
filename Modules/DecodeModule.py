import cv2
from PIL import Image
from PIL import ImageTk

import ffmpeg, av, io, pickle

@DeprecationWarning
def decode_h264(h264):

    return cv2.QuerryFrame(h264)

    #cv2.VideoCapture(h264)

    #

@DeprecationWarning  
def h264_to_label(label, h264):
    #print("foo")
    #print(h264)
    #tmp = cv2.QuerryFrame(h264)
    #print(h264)

    #ret,frame = cv2.VideoCapture(h264).read()
    #print(frame)

    #ret, frame = tmp.read()
    #print(tmp)
    print("test")
    decoded = pickle.loads(h264)
    frame = cv2.imdecode(decoded, cv2.IMREAD_COLOR)
    cv2.imshow("test", frame)

    '''
    print("a")
    rawData = io.BytesIO()
    rawData.write(h264)
    rawData.seek(0)
    try:
        container = av.open(rawData, format="h264", mode='r')
    except Exception as e: print(e)
    ''''''
    '''
    '''
    print("b")
    for packet in container.demux():
        print("c")
        if packet.size() == 0: continue
        for frame in packet.decode():
            print("a")
            imgtk = ImageTk.PhotoImage(image=frame)
            label.imgtk = imgtk
            label.configure(image=imgtk)
            '''
    '''
    #img = Image.fromarray(tmp)
    imgtk = ImageTk.PhotoImage(image=tmp)
    label.imgtk = imgtk
    label.configure(image=imgtk)
    '''

@DeprecationWarning
def foo(param):
    #a = Image.fromarray(param)
    print(param)