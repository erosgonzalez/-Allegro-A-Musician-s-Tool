import os
from flask import *
from emailing import SendEmail
from werkzeug.utils import secure_filename
from alsaausioTest import recordNotes
import wave
import pyaudio
import alsaaudio
import numpy as np
import aubio
import librosa

app = Flask(__name__)

UPLOAD_FOLDER = "soundfiles" #where the saved songs are sent to
ALLOWED_EXTENSIONS = set(["mp3", "wav"]) #only allows mp3s and waves
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER #the place where the opating system will save files

def allowed_file(filename):
    return "." in filename and \
            filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS#returns true if conditions are met

#-------------------------------------------------------------------------------
#This is the Python script for recording in the back end.

save = False #use for saving the recoridng
data = None
channel = 2
frames = []
rate = None
format = pyaudio.paInt16

@app.route("/record", methods = ["POST"])

#records, saves, and analyzes audio
def record():
    seconds = int(request.form["seconds"])
    file = open("notesPlayed.txt", 'w')
    index = 0

    global save, data, frames, channel, rate
    
    #audio consts
    samplerate = 44100
    buffSize = 2048
    hopSize = 1024
    framesize = 1024
    rate = samplerate
    time = 0
    secondsPassed = 1

    notesPlayed = []

    #pyaudio record and save
    FORMAT = pyaudio.paInt16
    WAVE_OUTPUT_FILENAME = "file.wav"
    dataSave = None

    audio = pyaudio.PyAudio()

    #open pyaudio stream
    stream = audio.open(format=FORMAT, channels=channel,
                	rate=samplerate, input=True,
                	frames_per_buffer=buffSize/2)
    
    #initializes audio for recording
    recorder = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE)
    recorder.setperiodsize(framesize)
    recorder.setrate(samplerate)
    recorder.setformat(alsaaudio.PCM_FORMAT_FLOAT_LE)
    recorder.setchannels(1)
    
    #sets up pitch detection
    pitchFind = aubio.pitch("default", buffSize, hopSize, samplerate)
    pitchFind.set_unit("Hz")
    # ignore frames under this level
    pitchFind.set_silence(-40)
    
    print "Recording..."
    
    
    # finds frequencies in given seconds
    for i in range(0, samplerate / hopSize * seconds):
	print "******", samplerate/ hopSize * seconds, "******"
	_, data = recorder.read()
	dataSave = stream.read(buffSize/2)
	frames.append(dataSave)
	# convert data to aubio float samples
	samples = np.fromstring(data, dtype=aubio.float_type)

	# pitch of current frame
	freq = pitchFind(samples)[0]
	energy = np.sum(samples*2)/len(samples)
	if freq > 0:
		notes = librosa.hz_to_note(freq)
		file.write(notes[0])
		file.write('\n')
		notesPlayed.append(notes[0])
		print freq, " ", notes[0]
		index =+ 1
	time += 1
	if time == 42 * secondsPassed:
		file.write("********Above played for 1 second********\n")
		secondsPassed += 1
    #close stream for pyaudio
    stream.stop_stream()
    stream.close()
    audio.terminate()

    #save file using pyaudio 
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(channel)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(samplerate)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    file.close()

    del frames[:]
    #del notesPlayed[:]
    print time
    time = 0
    secondsPassed = 0
    return render_template("convert_recording.html")

@app.route("/download_recording")
def download_recording():
    file = "soundfiles/temp.wav"
    file = wave.open(file, 'w')
    file.setnchannels(channel)
    file.setsampwidth(pyaudio.PyAudio().get_sample_size(format))
    file.setframerate(rate)
    file.writeframes(b''.join(frames))
    file.close
    download = '''<a href = "soundfiles/temp.wav" download>DOWNLOAD LINK</>'''
    del frames[:]
    return render_template("convert_recording.html", download = download)

def write_file():
    submit = '''<form action = "/get_file_name" method = "post">
                <input type = "text" name = "new_file" class = "user_file" placeholder = "File name...">
                <input type = "submit" value = "Submit"/>
            </form>'''
    return render_template("convert_recording.html", submit = submit)
    
app.jinja_env.globals.update(record = record, write_file = write_file)

#-------------------------------------------------------------------------------
@app.route("/")
def main():
    return render_template("main.html")
#-------------------------------------------------------------------------------
@app.route("/convert")
def convert():
    return render_template("convert.html")

@app.route("/convert_upload")
def convert_upload():
    return render_template("convert_upload.html")

@app.route("/convert_recording")
def convert_recording():
    return render_template("convert_recording.html")

@app.route("/option", methods = ["POST"])
def option():
    option = request.form["option"]
    if (option == "upload"):
        return redirect("/convert_upload")
    else:
        return redirect("/convert_recording")

@app.route("/upload_file", methods = ["POST"])
def getfile():
    file = request.files["sound_file"] #asks for the selected song
    if file and allowed_file(file.filename): #checks if its a valid and allowed extension
        filename = secure_filename(file.filename)
        
        if filename.endswith(".mp3") or filename.endswith(".wav"):
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename)) #stores in into the storage "filename"
            audio = '''<h1>Play - ''' + filename + '''</h1>
                    <audio controls>
                        <source src = "/soundfiles/''' + filename + ''' type = "audio/mp3">
                    </audio>'''
            button = '''<button>CONVERT</button>'''
            
            return render_template("convert_upload.html", audio = audio, button = button)
            
    else:
        invalid = '''<script> InvalidFile(); </script>'''
        return render_template("convert_upload.html", invalid = invalid)
    
    
#-------------------------------------------------------------------------------
@app.route("/tune")
def tune():
    return render_template("tune.html")
#-------------------------------------------------------------------------------
@app.route("/about")
def about():
    return render_template("about.html")
#-------------------------------------------------------------------------------
user_feedback = []
@app.route("/feedback")
def returnFeedback():
    feedback_dict = {"name1" : "", "comment1" : "", "name2" : "", "comment2" : "", "name3" : "",
                    "comment3" : "", "name4" : "", "comment4" : "", "name5" : "", "comment5" : "",
                    "name6" : "","comment6" : "", "name7" : "", "comment7" : "", "name8" : "",
                    "comment8" : "", "name9" : "","comment9" : "", "name10" : "", "comment10" : ""
                    }
    for i in range(len(user_feedback)):
        feedback_dict["name" + str(i+1)] = "Name: " + user_feedback[i][0]
        feedback_dict["comment" + str(i+1)] = "Comment: " + user_feedback[i][1]
        
    print feedback_dict
    return render_template("feedback.html", feedback_dict = feedback_dict)
#-------------------------------------------------------------------------------
#gets the entered name and feedback and adds it to the database, redirected to returnFeedback
@app.route("/get_feedback", methods = ["POST"])
def getFeedback():
    global user_feedback
    name = request.form["name"]
    comment = request.form["comment"]
    checkDataBase = []
    
    if name == "" or name == " ":
        return redirect("/feedback")
    elif comment == "" or comment == " ":
        return redirect("/feedback")
        
    with open("databases/feedback.txt", "rb") as file:
        checkDataBase = file.readlines()
    

    if name not in checkDataBase:
        if len(user_feedback) < 11:
            with open("databases/feedback.txt", "a") as file:
                file.write(str(name) + "\n")
                file.write(str(comment) + "\n")
            user_feedback.append([name, comment])
            
        elif len(user_feedback) >= 10:
            user_feedback.pop(0)
            user_feedback.append([name, comment])
    
    else:
        print "Name already in database!"
    
    return redirect("/feedback")
#-------------------------------------------------------------------------------
#removes the entered name and feedback, redirected to returnFeedback
@app.route("/remove_feedback", methods = ["POST"])
def removeFeedback():
    global user_feedback
    name = request.form["name"] + "\n"
    database = None
    
    with open("databases/feedback.txt", "rb") as file:
        database = file.readlines()
    
    inFeedback = False
    
    for pair in user_feedback:
        if name == pair[0]:
            inFeedback = True
            break
        
    if inFeedback and name in database:
        for i in range(len(user_feedback)):
            if user_feedback[i][0] == name:
                user_feedback.pop(i)
                print "Name found in user feedback and removed!"
                break
            
        for i in range(len(database)):
            if database[i] == name:
                database.pop(i)
                database.pop(i)
                print "Name found in database and removed!"
                break;
        
    elif not inFeedback and name in database:
        for i in range(len(database)):
            if database[i] == name:
                database.remove(database[i])
                database.remove(database[i])
                break
    else:
        print "Name not found!"
    
    with open("databases/feedback.txt", "wb") as file:
        for nameorcomment in database:
            file.write(nameorcomment)
        
        del user_feedback[:]
        for i in range(len(database)-1):
            user_feedback.append((database[i], database[i+1]))
    
    return redirect("/feedback")
#-------------------------------------------------------------------------------
@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/contact", methods = ["POST"])
def contact_us():
    subject = request.form["subject"]
    email = request.form["email"]
    print subject
    print email
    
    
    #C9 Does not allow smtp access, but this works
    x = SendEmail("allegro.soundtonotation@gmail.com", "cst205project3!", "allegro.soundtonotation@gmail.com",
                  "", str(email), str(subject))
    x.Send()
    
    return render_template("contact.html")
    
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(
    port = int(os.getenv('PORT', 8080)),
    host = os.getenv('IP', '0.0.0.0'),
    debug = True
)
