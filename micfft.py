import pyaudio
import numpy as np
import wave
from time import time
from threading import Thread

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

CHUNK = 2048 # RATE / number of updates per second

lastFft = {'val': 0, 'freq': 0, 'time': 0}

def nextFft(stream):
	data = stream.read(CHUNK, exception_on_overflow=False)
	waveData = wave.struct.unpack("%dh"%(CHUNK), data)
	npArrayData = np.array(waveData)
	return np.abs(np.fft.rfft(npArrayData))

def getMax(fftData):
	which = fftData[1:].argmax() + 1
	# use quadratic interpolation around the max
	if which != len(fftData)-1:
		y0,y1,y2 = np.log(fftData[which-1:which+2:])
		x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
		# find the frequency and output it
		thefreq = (which+x1)*RATE/CHUNK
		theval = fftData[which]
		return theval, thefreq
	else:
		thefreq = which*RATE/CHUNK
		theval = fftData[which]
		return theval, thefreq

def micFftLoop():
	p=pyaudio.PyAudio()
	stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True, frames_per_buffer=CHUNK)
	running = True
	while running:
		try:
			fftData = nextFft(stream)
			theval, thefreq = getMax(fftData)
			lastFft['val'] = theval
			lastFft['freq'] = thefreq
			lastFft['time'] = time()
#			print('new fft data', round(theval))
		except KeyboardInterrupt:
			print('Mic Fft Thread Interrupted')
			running = False
	stream.stop_stream()
	stream.close()
	p.terminate()

Thread(target=micFftLoop, daemon=True).start()
