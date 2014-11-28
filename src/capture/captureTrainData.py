#Allows for relative import
import sys, os, argparse, random, uuid, time
import pygame
sys.path.append(os.path.abspath("../"))

from utils.streamUtils.StreamRead import StreamRead

class main():
	def __init__(self, inputArgs):
		self.debug = inputArgs.debug

		# Value to determine how long to wait for hold gestures, and how many
		# samples to take for explicit gestures
		self.numSamples = 5
		# Timeout for taking explicit samples
		self.ExplTimeout = 3

		# Center the window on the screen
		os.environ['SDL_VIDEO_CENTERED']  = '1'
		pygame.init()
	 	size = width, height = 1500, 800
	 	speed = [2, 2]
	 	black = 0, 0, 0
	 	self.screen = pygame.display.set_mode(size)
	 	pygame.display.set_caption('smartShoes Data capture')
	 	# Fill background
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill((250, 250, 250))

		# Blit everything to the screen
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()

	 	# Open input file
		if not self.debug:
			self.stream = StreamRead(inputArgs.streamFile)

		self.gesture_classes = [{
								"className" : "REST",
								"type" : "HOLD",
								"desc" : "keep your feet at rest"},
								{
								"className" : "LEFT-FOOT-STOMP",
								"type" : "EXPL",
								"desc" : "stamp your left foot"},
								{
								"className" : "LEFT-TOE-UP",
								"type" : "HOLD",
								"desc" : "raise your left toe while your heel is on the ground"},
								{
								"className" : "LEFT-TOE-TAP",
								"type" : "EXPL",
								"desc" : "tap your left toe once"},
								{
								"className" : "LEFT-HEEL-TAP",
								"type" : "EXPL",
								"desc" : "tap your left heel once"},
								{
								"className" : "LEFT-HEEL-RAISE",
								"type" : "HOLD",
								"desc" : "raise your left heel"},
								{
								"className" : "LEFT-FOOT-FLICKLEFT",
								"type" : "EXPL",
								"desc" : "flick your left foot to the left"},
								{
								"className" : "LEFT-FOOT-FLICKRIGHT",
								"type" : "EXPL",
								"desc" : "flick your left foot to the right"},
								{
								"className" : "LEFT-FOOT-SPINCW",
								"type" : "EXPL",
								"desc" : "spin your left foot clockwise"},
								{
								"className" : "LEFT-FOOT-SPINACW",
								"type" : "EXPL",
								"desc" : "spin your left foot anticlockwise"},
								]

		#generate trial orders
		trials = self.genTrials(inputArgs.num_trials)

		#run trials
		for trial in trials:
			print "Capturing Gesture:", trial["className"]
			if trial["type"] == "HOLD":
				self.captureHold(inputArgs.DIR, trial["className"], trial["desc"])
				self.endTrial()
			else:
				# Explicit gesture movement
				for i in xrange(0, self.numSamples):
					self.captureExplicit(inputArgs.DIR, trial["className"], trial["desc"])
					self.endTrial()


	## Utility Methods ##

	#generate a random ordering of trials
	def genTrials(self, num_trials):
		trials  = []
		for c in self.gesture_classes:
			for i in xrange(0, num_trials):
				trials.append(c)

		random.shuffle(trials)
		return trials

	#Write test message to screen
	def textToScreen(self, text, y_pos=10):
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill((250, 250, 250))
		font = pygame.font.Font(None, 28)
		text = font.render(text, 1, (10, 10, 10))
		textpos = text.get_rect()
		textpos.centerx = self.background.get_rect().centerx
		self.background.blit(text, textpos)
		self.screen.blit(self.background, (0, y_pos))
		pygame.display.flip()

	#Display message and wait for next test
	def endTrial(self):
		self.textToScreen("Thank you. Please rest your feet and wait for the next test.")
		time.sleep(2)

	## File Utilities ##

	#make data file with Class name an Uniqie ID
	def makeFile(self, dir_name, class_name):
		return file(os.path.join(dir_name, class_name + '_' + str(uuid.uuid1()) + '.csv'), 'w+')

	#Write list of data points to file
	def writeData(self, file, data):
		enc_data = ','.join(map(str,data)) + '\n'
		file.write(enc_data)

	## Trial Methods ##
	# Base capture method - Press space, do gesture and hold
	def captureHold(self, dir_name, gesture, displayText):
		self.textToScreen("Press SPACE, " + displayText + ", and hold for the next " + str(self.numSamples) + " seconds")
		ready = False

		# Wait for user to begin test
		while not ready:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN :
					if event.key == pygame.K_SPACE :
						ready = True

		if self.debug:
			for i in xrange(0, self.numSamples):
				self.textToScreen("Please wait " + str(self.numSamples-i) + " seconds")
				# Don't capture data
				time.sleep(1)
			return

		# Capture data for as long as holdLength (seconds)
		for i in xrange(0, self.numSamples):
			self.textToScreen("Please wait " + str(self.numSamples-i) + " seconds")
			output_file = self.makeFile(dir_name, gesture)
			self.stream.emptyStreamBuffer()
			stop = time.time() + 1
			while time.time() < stop:
				records = self.stream.readFromStream()
				for record in records:
					self.writeData(output_file, record)

	# Base capture method - Press space, do gesture, then press space
	def captureExplicit(self, dir_name, gesture, displayText):
		self.textToScreen("Press SPACE, " + displayText + ", and then press SPACE as soon as you are done")

		if not self.debug:
			output_file = self.makeFile(dir_name, gesture)

		ready = False
		done = False

		# Wait for user to begin test
		while not ready:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN :
					if event.key == pygame.K_SPACE :
						ready = True
						startTime = time.time()

		if not self.debug:
			self.stream.emptyStreamBuffer()

		self.textToScreen(displayText + ", and then press SPACE as soon as you are done")
		# Capture data until space is pressed or reached timeout
		while not done and time.time() < startTime+self.ExplTimeout :
			if not self.debug:
				records = self.stream.readFromStream()
				for record in records:
					self.writeData(output_file, record)

			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN :
					# Check that we've captured data for at least half a second before quitting
					if event.key == pygame.K_SPACE and time.time() > startTime+0.5 :
						done = True

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Capture traing data for smartshoes")
	parser.add_argument("-dir", action = "store", default = "/blahblah", dest = "DIR",  type = str, help = "The directory to store captured data in")
	parser.add_argument("-d", action = "store_true", dest = "debug", help = "Turn debug mode on (run without hardware device)")
	parser.add_argument("-n", action = "store", default = 5, type = int, dest = "num_trials", help = "The Number of times to capture data for each gesture")
	parser.add_argument("-s", action = "store", default = "/dev/input/smartshoes", type = str, dest = "streamFile", help = "The Name of the stream to read input from (default: /dev/input/smartshoes)")
	inputArgs = parser.parse_args()
	if not inputArgs.debug and inputArgs.DIR == "/blahblah":
		print("Error: Must have -dir (directory) set if not in -d (DEBUG) mode")
		sys.exit(1)
	if inputArgs.debug:
		print("DEBUG MODE ENABLED")
	main(inputArgs)
