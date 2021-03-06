#Allows for relative import
import sys, os, argparse, random, uuid, time
import pygame
sys.path.append(os.path.abspath("../"))

from utils.streamUtils.StreamRead import StreamRead
from receiver import calibration

class main():
	def __init__(self, inputArgs):
		self.debug = inputArgs.debug
		exclude_idxs = [9]
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
	 	pygame.display.set_caption('FootGest Data capture')
	 	# Fill background
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill((250, 250, 250))

		# Blit everything to the screen
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()
		#self.c = calibration.Calibration()

	 	# Open input file
		if not self.debug:
			self.stream = StreamRead(inputArgs.streamFile, exclude_indexes = exclude_idxs)

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
		sleepEnd = time.time() + 2
		while time.time() < sleepEnd:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN :
					# Means that spaces don't carry over to next trial
					pass

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
		mov = GestVid(gesture, self.screen)

		ready = False

		# Wait for user to begin test
		while not ready:
			mov.update()
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
			#output_file_calibrated = self.makeFile(dir_name + "_calib", gesture)
			self.stream.emptyStreamBuffer()
			stop = time.time() + 1
			while time.time() < stop:
				records = self.stream.readFromStream()
				for record in records:
					self.writeData(output_file, record)
					#if len(record) < 9:
					#	self.writeData(output_file_calibrated, record)
					#else:
					#	self.writeData(output_file_calibrated, list(self.c.process(*[float(i) for i in record])))

# Base capture method - Press space, do gesture, then press space
	def captureExplicit(self, dir_name, gesture, displayText):
		self.textToScreen("Press SPACE, " + displayText + ", and then press SPACE as soon as you are done")

		mov = GestVid(gesture, self.screen)

		if not self.debug:
			output_file = self.makeFile(dir_name, gesture)
			#output_file_calibrated = self.makeFile(dir_name + "_calib", gesture)

		ready = False
		done = False

		# Wait for user to begin test
		while not ready:
			mov.update()
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
					#if len(record) < 9:
					#	self.writeData(output_file_calibrated, record)
					#else:
					#	self.writeData(output_file_calibrated, list(self.c.process(*[float(i) for i in record])))

			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN :
					# Check that we've captured data for at least 0.3 seconds before quitting
					if event.key == pygame.K_SPACE and time.time() > startTime+0.3 :
						done = True

class GestVid:
	def __init__(self, gesture, screen):
		self.mov = pygame.movie.Movie("images/" + gesture + ".mpg")
		if not self.mov.has_video():
			print("Video file for " + gesture + " is invalid.")
			sys.exit(1)
		mov_size = self.mov.get_size()

		self.background = pygame.Surface(mov_size)
		self.background = self.background.convert()
		self.background.fill((250, 250, 250))

		self.screen = screen
		self.pos = (self.screen.get_size()[0]/2) - (mov_size[0]/2), (self.screen.get_size()[1]/2) - (mov_size[1]/2)

		self.mov_screen = pygame.Surface(mov_size).convert()
		self.mov.set_display(self.mov_screen)
		self.mov.play()

	def update(self):
		self.screen.blit(self.mov_screen, self.pos)
		pygame.display.update()
		if not self.mov.get_busy():
			self.mov.rewind()
			self.mov.set_display(None)
			self.screen.blit(self.background, self.pos)
			pygame.display.update()
			time.sleep(0.5)
			self.mov.set_display(self.mov_screen)
			self.screen.blit(self.mov_screen, self.pos)
			pygame.display.update()
			self.mov.play()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Capture traing data for the FootGest device")
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
