import Tkinter as tk
import ttk
import pyaudio
import wave
import os
import subprocess
from tkFileDialog import askopenfilenames
import tkMessageBox
from PIL import Image, ImageTk
import datetime

#MIGHT NEED TO CONVERT mp3 INTO WAV

root = tk.Tk()
#this gets the width and height from the current window
screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
#this then sets the height and disables top menu
root.overrideredirect(1)
root.geometry('%dx%d+0+0' % (screen_width, screen_height))
print ("Width: " + str(screen_width), "Height: " + str(screen_height))        
#div by 2 to test window stuffs
#USE GRID INSTEAD OF PACK

#root.withdraw() hides to main window
#root.deiconify() shows the main window
waveNames = ["%d.wav" % d for d in range(50)] #creates a list of possible wav names (will be used to write them and check for doubles)
filenames = [] #for selected files
loginInfo = {"Andy Kor": "hello"}
correct = False
x = 0
y = 0
record_time = 0

#--------------------------------------------------------------------------------------------------------------------------------------
'''
class Login:
    def __init__(self):
        global root
        root.withdraw()
        self.root = tk.Tk()
        
    def check(self):
        first = tk.Button(self.root, text = "Create Account", height = 25, width = 50)
        enter = tk.Button(self.root, text = "Existing User", height = 25, width = 50, command = self.login)
        enter.pack()
        first.pack()
        
    def login(self):
        self.root.withdraw()
        self.x = tk.Tk()
        v = tk.StringVar()
        d = tk.StringVar()
        self.x.minsize(width = 200, height = 45)
        name = tk.Label(self.x, text = "Name:")
        password = tk.Label(self.x, text = "Password:")
        self.nameEntry = tk.Entry(self.x, textvariable = v)
        self.passwordEntry = tk.Entry(self.x, textvariable = d, show = "*")
        submit = tk.Button(self.x, text = "Submit", command = self.entry)

        name.grid(row = 0)
        password.grid(row = 1)
        self.nameEntry.grid(row = 0, column = 1)
        self.passwordEntry.grid(row = 1, column = 1)
        submit.grid(row = 2, column = 1)

    def entry(self):
        name = self.nameEntry.get()
        password = self.passwordEntry.get()
        if name in loginInfo:
            if loginInfo[name] == password:
                self.x.withdraw()
                root.deiconify()
            else:
                tkMessageBox.showinfo(message = "Incorrect password!")
        if name not in loginInfo:
            tkMessageBox.showinfo(message = "Register this account!")
            self.check()
    
Login().check()
'''
#--------------------------------------------------------------------------------------------------------------------------------------

class Convert:
    def __init__(self):
        while True:
            uploadedfilenames = askopenfilenames(multiple = True)
            mp3 = None
            if (uploadedfilenames == ''):
                tkMessageBox.showinfo(message = "File upload has been cancelled, program will stop.")
            if (uploadedfilenames.endswith(".wav")):
                tkMessageBox.showinfo(message = "This is already a .wav file!")
            if uploadedfilenames.endswith(".mp3"):
                mp3 = root.splitlist(uploadedfilenames)
                
#--------------------------------------------------------------------------------------------------------------------------------------

class GetFile:
    def __init__(self):
        global filenames
        self.file = None
        
    def fileUpload(self):
        while True:
            uploadedfilenames = askopenfilenames(multiple = True)
            if uploadedfilenames == '':
                tkMessageBox.showinfo(message = "File upload has been cancelled, program will stop.")
                return 0 #ensures that they are not caught in a loop
            
            if uploadedfilenames.endswith(".wav"):
                self.file = root.splitlist(uploadedfilenames)
                return self.file
            
            if uploadedfilenames.endswith(".mp3"):
                tkMessageBox.showinfo(message = "Not a wav file! Convert this first!")
                
            else:
                tkMessageBox.showinfo(message = "This is not a wave file!")
                return 0 #ensures that they are not caught in a loop
        
    def saveFile(self):
        if (self.file == None):
            tkMessageBox.showinfo(message = "No file selected!")
        else:    
            filenames.append(self.file)
#--------------------------------------------------------------------------------------------------------------------------------------
class RecordingProgress:
    def __init__(self):
        global record_time
        self.progress = ttk.Progressbar(root, orient = "horizontal", length = 200, mode = "determinate")
        self.progress.pack()
        self.recording_time = 0
        self.max_recording_time = 0
        
    def start(self):
        self.progress["value"] = 0
        self.max_recording_time = record_time
        self.progress["maximum"] = record_time
        self.update()
        
    def update(self):
        self.recording_time += 1
        self.progress["value"] = self.recording_time
        if self.recording_time < self.max_recording_time:
            root.after(100, self.update())
#--------------------------------------------------------------------------------------------------------------------------------------
class Record:
    def __init__(self, CHUNK_SIZE, FORMAT, RATE, CHANNELS, RECORD_SECONDS):
        self.audio = pyaudio.PyAudio()
        self.chunk = CHUNK_SIZE
        self.format = FORMAT
        self.rate = RATE
        self.channel = CHANNELS
        self.seconds = RECORD_SECONDS
        self.data = 0
        self.frames = []
        self.current_file = ""
        self.progress = RecordingProgress()

    def start(self):
        self.startRecording()
        self.progress.start()
        
    def startRecording(self):
        time_elapsed = []
        count = 0
        
        tkMessageBox.showinfo(message = "Recordings will only last 1 minute!")
        #getting an error with the kwargs for the open method
        stream = self.audio.open(format = self.format,
                                 channels = self.channel,
                                 rate = self.rate,
                                 input = True,
                                 frames_per_buffer = self.chunk)
        
        chunks = int(self.rate/(self.chunk * self.seconds))
        
        tkMessageBox.showinfo(message = "Confirm to record.")
        print "Recording..."
        for i in range(0, chunks):
            self.data = stream.read(self.chunk, exception_on_overflow = False)
            self.frames.append(self.data)
            hour = datetime.datetime.now().hour % 12
            minute = datetime.datetime.now().minute
            second = datetime.datetime.now().second
            time = str(hour) + ":" + str(minute) + ":" + str(second)
            if time in time_elapsed:
                continue
            else:
                time_elapsed.append(time)
                count += 1
                record_time += 1
                print "Time elapsed: %d seconds." % count
            
        stream.stop_stream()
        stream.close()
        self.audio.terminate()
        print "Done recording!"
        tkMessageBox.showinfo(message = "Done recording!")
        
    #callback error for delrecording and delsavedrecording
    def delRecording(self):
        if len(self.frames) > 0:
            self.data = 0
            del self.frames[:]
            self.current_file = ""
            tkMessageBox.showinfo(message = "Recording deleted!")
        else:
            tkMessageBox.showinfo(message = "Nothing has been recorded!")
        
            
    def delSavedRecording(self):
        if (self.current_file == ""):
            tkMessageBox.showinfo(message = "No saved recording to delete!")
        else:
            os.remove(self.current_file)
            tkMessageBox.showinfo(message = "File Deleted!")
            self.data = 0
            del self.frames[:]
            self.current_file = ""
            print "File Deleted!"
        
    def saveRecording(self):
        if len(self.frames) > 0:
            usedFiles = [i for i in os.listdir('.') if i[0].isdigit() and i.endswith(".wav")]
            j = 0
            if waveNames[j] in usedFiles:
                j += 1
            else:
                w = wave.open(waveNames[j], 'w')
                usedFiles.append(waveNames[j])
                w.setnchannels(self.channel)
                w.setsampwidth(self.audio.get_sample_size(self.format))
                w.setframerate(self.rate)
                w.writeframes(b''.join(self.frames))
                w.close
                self.current_file = waveNames[j]
                print self.current_file
            tkMessageBox.showinfo(message = "Recording has been saved!")
            
        else:
            tkMessageBox.showinfo(message = "Nothing to save!")
                
#--------------------------------------------------------------------------------------------------------------------------------------

class MainPage:
    def __init__(self):
        self.record = Record(1024, pyaudio.paInt16, 44100, 1, .01)
        # .01 = 100 seconds
        # .5 = 3 seconds
        self.uploadFile = GetFile()

    def printcoor(self, event):
        self.x = event.x
        self.y = event.y
        #check all picture positions and initiate command here
        print (self.x, self.y)

    def Background(self):
        load = Image.open('background.png')
        render = ImageTk.PhotoImage(load)
        img = tk.Label(root, image = render)
        img.image = render
        img.place(x = 0, y = 0)
        
    def Main(self):
        root.bind("<Button 1>", self.printcoor)
        '''
        upload = Image.open('upload.png')
        render_upload = ImageTk.PhotoImage(upload)
        img1 = tk.Label(root, image = render_upload)
        img1.image = render_upload
        img1.place(x = 100, y = 100)
        '''
        
        
        upload = tk.Button(root, text = "Upload File", command = self.uploadFile.fileUpload)
        start = tk.Button(root, text = "Start Recording", command = self.record.start)
        delete = tk.Button(root, text = "Delete Recording", command = self.record.delRecording)
        save = tk.Button(root, text = "Save Recording", command = self.record.saveRecording)
        deletes = tk.Button(root, text = "Delete Saved Recording", command = self.record.delSavedRecording)
        quit_program = tk.Button(root, text = "Quit", command = root.destroy)

        upload.pack()
        start.pack()
        delete.pack()
        save.pack()
        deletes.pack()
        quit_program.pack()
        

MainPage().Background()
MainPage().Main()


root.mainloop()