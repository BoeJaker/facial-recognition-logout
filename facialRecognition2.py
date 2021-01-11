import cv2
import sys
import wmi
import keyboard
import ctypes

cascPath = 'C:\\Users\\Lenovo\\Google Drive\\Workspace - old\\Backups\\10.42.0.1\\Programming\\Python\\OpenCV\\opencv\\data\\haarcascades_cuda\\haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascPath)

video_capture = cv2.VideoCapture(0)

countdown = 250

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    try:
        if faces[0].any():
            countdown = 250
            wmi.WMI(namespace='wmi').WmiMonitorBrightnessMethods()[0].WmiSetBrightness(100, 0)
    except:
        countdown = countdown - 1
        if countdown == 0:
            countdown = 250
            wmi.WMI(namespace='wmi').WmiMonitorBrightnessMethods()[0].WmiSetBrightness(25, 0)
            ctypes.windll.user32.LockWorkStation()
    
    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('q'):  # if key 'q' is pressed 
            print('You Pressed A Key!')
            break  # finishing the loop
    except:
        break  # if user pressed a key other than the given key the loop will break
    # Display the resulting frame
    # cv2.imshow('Video', frame)

    # if cv2.waitKey(1) & 0xFF == ord('q'):
        # break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()