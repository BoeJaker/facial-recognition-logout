# This is a facial recognition lock for windows 10 PCs. It includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.
#   3. Only running face detection once per second
#
# To run this program type:
# pythonw.exe "C:\Users\Lenovo\git\facial-recognition-logout\Facial_Recognition_V4.py"
# into the powershell prompt
#

# Sys tray
import pystray
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image, ImageDraw

# Face recognition
import face_recognition, cv2
import numpy as np

# Tools
from datetime import datetime
import time
import keyboard 
import wmi
import ctypes
import easygui
import pathlib

# Modules
# import keyboardlock

path = str(pathlib.Path(__file__).parent.absolute()) # Do not change

# Paths to icon, user images and captures - change as necesary
icon_location = path+"\\Private\\bat1.png"
user_image_location = path+"\\Private\\baker.jpg"
captures_location = path+"\\Private\\Unknowns\\"

# Control varibles
passw = "adalovelace" # optional, leave blank for no auth
user = "boejaker" 
delay = 1.2 # sets delay between scans (seconds) scale is from 0 to 2
counter = 100
decrement = 10 # sets the amount the conuter is decremented by scale is from 1 to 20 (10 is default)
threshold = 2 # sets when the diming kicks in scale of 2 to 5
dim = True # Sets wether the display dims based on users presence
dim_mid = 25 # sets screen brightness on medium activity
dim_low = 0 # set screen brightness on low / suspicious activity

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)
# Initailize ret and frame globally
ret = 0 ; frame = 0

clamp = lambda n, minn, maxn: max(min(maxn, n), minn)

pause = False

# Stop all processes & exits
def password(msg, fieldNames):
    if passw:
        title = "Facial recognition authorization"
        return easygui.multpasswordbox(msg, title, fieldNames)
    return user, passw
    
def stop():
    p = password("Enter credentials to stop program", ["User", "Password"])
    if p[1] == passw and p[0] == user:
        try:
            cv2.destroyAllWindows() 
            video_capture.release()
            icon.stop()
            exit()
        except:
            return True
    return False

def pause_loop():
    global pause
    p = password("Enter credentials to pause program", ["User", "Password"])
    if p[1] == passw and p[0] == user:
        if pause is True: pause = False
        if pause is False: pause = True

def start():
    pass

# Menu option to view webcam
def view():
    while True:
        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

# Main Loop
#################################
def callback(icon):
    
    countdown = counter # Initialize lock countdown
    # block = keyboardlock.blockInput()

    # Load a users picture and learn how to recognize it.
    baker_image = face_recognition.load_image_file(user_image_location) # Change this file path to match your selfie files location
    baker_face_encoding = face_recognition.face_encodings(baker_image)[0]

    # Create arrays of known face encodings and their names
    known_face_encodings = [
        baker_face_encoding,
    ]
    known_face_names = [
        "Joe Baker",
    ]
    # Initialize some variables
    global ret
    global frame
    global pause
    
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    
    image = Image.new('RGBA', (128,128), (255,255,255,255)) # create new image

    try:
        while True:
            if pause is False:
                # Grab a single frame of video
                ret, frame = video_capture.read()
        
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        
                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]
        
                # Only process every other frame of video to save time
                if process_this_frame:
                    # Find all the faces and face encodings in the current frame of video
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
                    face_names = []
                    for face_encoding in face_encodings:
                        # See if the face is a match for the known face(s)
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                        name = "Unknown"
        
                        # # If a match was found in known_face_encodings, just use the first one.
                        # if True in matches:
                        #     first_match_index = matches.index(True)
                        #     name = known_face_names[first_match_index]
        
                        # Or instead, use the known face with the smallest distance to the new face
                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]
        
                        face_names.append(name)
        
                process_this_frame = not process_this_frame
        
                # Display the results
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
        
                    # Draw a box around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        
                    # Draw a label with a name below the face
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        #           print(top, right, bottom, left)
        #           if bottom - top <= 150:
        #              countdown = countdown - decrement
        
                # Face fecognition state machine:
                # Based on detected faces and a countdown. The following dims / brightens 
                #  the screen and / or locks the workstation
                try:
                    countdown = countdown + 1
                    if face_names[0] == 'Joe Baker': # If The users face is detected
                        countdown = counter # reset countdown
#                         block.unblock()
                        wmi.WMI(namespace='wmi').WmiMonitorBrightnessMethods()[0].WmiSetBrightness(100, 0) # Change brightness back to max
        
                    elif face_names[0] == 'Unknown': # If an unknown face is detected
                        dateTimeObj = datetime.now()
                        dt = str(dateTimeObj.year)+str(dateTimeObj.month)+str(dateTimeObj.day)+str(dateTimeObj.hour)+str(dateTimeObj.minute)+str(dateTimeObj.second)
                        cv2.imwrite(captures_location+"Unknown"+dt+".jpg", frame)
#                         block.block()
                        wmi.WMI(namespace='wmi').WmiMonitorBrightnessMethods()[0].WmiSetBrightness(dim_low, 0) # Dim screen
                        ctypes.windll.user32.LockWorkStation() # Lock workstation
        
                except: #If no face detected
                    countdown = countdown - decrement # Decrement 'debounce' countdown
                    if countdown <= 0: # If user has gone
#                         block.block()
                        ctypes.windll.user32.LockWorkStation() # Lock workstation
                    elif countdown <= counter/threshold: # If user has looked away
                        wmi.WMI(namespace='wmi').WmiMonitorBrightnessMethods()[0].WmiSetBrightness(dim_mid, 0) # Partially dim screen
                
                # Update icon based on lock countdown
                img = image.copy()
                d = ImageDraw.Draw(img)
                d.rectangle([0, 128, 128, 128-(countdown * 128) / 100], fill='black')
                icon.icon = img
                
                clamp(countdown,0,counter)
            time.sleep(delay)
            try:  # used try so that if user pressed other than the given key error will not be shown
                if keyboard.is_pressed('q'):  # if key 'q' is pressed 
                    print('You Pressed A Key!')
                    if stop() : break  # finishing the loop
            except:
                if stop() : break # if user pressed a key other than the given key the loop will break
                
    except:
        pass
    
    # Release handle to the webcam once the while loop is broken
    video_capture.release()
    cv2.destroyAllWindows()
    icon.stop()

# Sys tray icon setup
# Set base image (needs changing to blank white square)
image = Image.open(icon_location) # Change this file path to match your icon files location
# Add menu options
menu = ( item('view', lambda :  view()),item('pause/start', lambda :  pause_loop()), item('close', lambda :  stop()) )
# Set sys tray icon parameters
icon = pystray.Icon("Test Icon 1", image, "Facial Lock", menu)

# Build sys tray icon
icon.visible = True
icon.run(setup=callback)
# Stop sys tray icon
