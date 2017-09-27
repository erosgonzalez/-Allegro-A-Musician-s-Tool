import alsaaudio
import numpy as np
import aubio
import librosa

def recordNotes(secs):
	#audio consts
	samplerate = 44100
	buffSize = 2048
	hopSize = 1024
	framesize = 1024
	seconds = secs

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
		_, data = recorder.read()
		# convert data to aubio float samples
		samples = np.fromstring(data, dtype=aubio.float_type)
		# pitch of current frame
		freq = pitchFind(samples)[0]
		energy = np.sum(samples*2)/len(samples)
		if freq > 0:
			notes = librosa.hz_to_note(freq)
			print freq, " ", notes[0]


