from DmxPy import DmxPy
dmx = DmxPy('COM4') # hard coded for now

def setColor(color, channel):
	for i in range(0, 4):
		dmx.setChannel(channel + i, color[i])

def render():
	dmx.render()

def blackout():
	dmx.blackout()
	dmx.render()
