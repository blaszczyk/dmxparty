from micfft import lastFft
#from mockfft import lastFft
import time
import math
from pardmx import *
#from mockdmx import *
import sys
import json

TIMESTEP = 0.01

def loadjson(filename):
	with open(filename) as json_file:
		return json.load(json_file)
		
COLORS = loadjson('colors.json')
COLORSETS = loadjson('colorsets.json')

def getColors(name):
	if name in COLORSETS:
		return [COLORS[c] for c in COLORSETS[name]]
	if name in COLORS:
		return [COLORS[name]]

def mix(color1, color2, ratio):
	def m(n):
		return round(color1[n] * (1 - ratio) + color2[n] * ratio)
	return (m(0), m(1), m(2), m(3))

def computeColor(cycle, colors, phase):
	colcount = len(colors)
	progress = (time.time() / cycle + phase) % 1
	colnr = math.floor(progress * colcount)
	ratio = (progress * colcount) % 1
	if colnr == colcount - 1:
		return mix(colors[colnr], colors[0], ratio)
	else:
		return mix(colors[colnr], colors[colnr+1], ratio)

def renderColors(programs):
	theval, thefreq = lastFft['val'], lastFft['freq']
	colval = round(theval / 3000000)
	currentTime = time.time()
	for program in programs:
		def getor(key, deflt=False):
			if key in program:
				return program[key]
			else:
				return deflt
		for idx, lamp in enumerate(program['lamps']):
			colors = program['colors']
			cycle = program['cycle']
			phase = idx/len(program['lamps'])
			color = computeColor(cycle, colors, phase)
			if getor('usefft'):
				fftval = lastFft['val'] / 3000000
				fftcolors = getor('fftcolors', colors)
				fftphase = getor('fftphase', 0)
				fftcolor = computeColor(cycle, fftcolors, phase + fftphase)
				color = mix(fftcolor, color, fftval)
			if getor('strobo'):
				stroborate = program['stroborate']
				strobophase = getor('strobophase', 0)
				strobothresh = getor('strobothresh', 0.5)
				if (currentTime / stroborate + strobophase * idx) % 1 < strobothresh:
					color = (0,0,0,0)
					color = computeColor(cycle, getor('strobocol', (0,0,0,0)), phase)
			setColor(color, lamp)
	render()

def loadProg(filename):
	programs = loadjson(filename)
	for program in programs:
		program['colors'] = getColors(program['palette'])
		if 'fftpalette' in program:
			program['fftcolors'] = getColors(program['fftpalette'])
		if 'strobocol' in program:
			program['strobocol'] = getColors(program['strobocol'])
	return programs

if __name__=="__main__":
	programs = loadProg(sys.argv[1])
	running = True
	print('Party started')
	lasttime = time.time()
	while running:
		try:
			renderColors(programs)
			nexttime = time.time()
			sleeptime = TIMESTEP - nexttime + lasttime
			lasttime = nexttime
			if sleeptime > 0:
				time.sleep(sleeptime)
		except KeyboardInterrupt:
			print('Party interrupted')
			running = False
