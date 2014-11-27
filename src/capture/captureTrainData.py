#Allows for relative import
import sys, os, argparse, random, uuid, time
import pygame
sys.path.append(os.path.abspath("../"))

from utils.streamUtils.StreamRead import StreamRead

class main():
	def __init__(self, inputArgs):
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

	 	#open stream reader
		self.stream = StreamRead(inputArgs.streamFile)

		self.gesture_classes = {"REST" : self.captureREST,
		 						"LEFT-FOOT-STOMP" : self.captureLEFT_FOOT_STOMP,
								"LEFT-TOE-UP" : self.captureLEFT_TOE_UP,
								"LEFT-TOE-TAP" : self.captureLEFT_TOE_TAP,
								"LEFT-HEEL-TAP" : self.captureLEFT_HEEL_TAP,
								"LEFT-HEEL-RAISE" : self.captureLEFT_HEEL_RAISE,
								"LEFT-FOOT-FLICKLEFT" : self.captureLEFT_FOOT_FLICKLEFT,
								"LEFT-FOOT-FLICKRIGHT" : self.captureLEFT_FOOT_FLICKRIGHT,
								"LEFT-FOOT-SPINCW" : self.captureLEFT_FOOT_SPINCW,
								"LEFT-FOOT-SPINACW" : self.captureLEFT_FOOT_SPINACW}
		#generate trial orders
		trials = self.genTrials(inputArgs.num_trials)

		#run trials
		for trial in trials:
			print "Capturing Gesture:", trial
			self.gesture_classes[trial](inputArgs.DIR)
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
	# Base capture method - Press space, do gesture and hold for specified time
	def captureHold(self, dir_name, gesture, displayText, holdLength):
		self.textToScreen(displayText)
		ready = False

		# Wait for user to begin test
		while not ready:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN :
					if event.key == pygame.K_SPACE :
						ready = True

		self.textToScreen("Please wait " + str(holdLength) + " seconds")

		# Capture data for as long as holdLength (seconds)
		for i in xrange(0, holdLength):
			output_file = self.makeFile(dir_name, gesture)
			self.stream.emptyStreamBuffer()
			stop = time.time() + 1
			while time.time() < stop:
				records = self.stream.readFromStream()
				for record in records:
					self.writeData(output_file, record)

	# Base capture method - Press space, do gesture, then press space
	def captureExplicit(self, dir_name, gesture, displayText):
		for i in xrange(1, 5):
			self.textToScreen(displayText)

			output_file = self.makeFile(dir_name, gesture)

			ready = False
			done = False

			# Wait for user to begin test
			while not ready:
				for event in pygame.event.get():
					if event.type == pygame.KEYDOWN :
						if event.key == pygame.K_SPACE :
							ready = True

			self.stream.emptyStreamBuffer()
			# Capture data until space is pressed
			while not done:
				records = self.stream.readFromStream()
				for record in records:
					self.writeData(output_file, record)

				for event in pygame.event.get():
					if event.type == pygame.KEYDOWN :
						if event.key == pygame.K_SPACE :
							done = True

	# Capture resting gesture for 5 seconds
	def captureREST(self, dir_name):
		displayText = "Press SPACE and then keep your feet at rest for the next 5 seconds"
		self.captureHold(dir_name, "REST", displayText, 5)

	# Capture left foot stomp gesture
	def captureLEFT_FOOT_STOMP(self, dir_name):
		displayText = "Press SPACE, Stamp your left foot and then press SPACE as soon as you are done"
		self.captureExplicit(dir_name, "LEFT-FOOT-STOMP", displayText)

	# Capture toe lifted
	def captureLEFT_TOE_UP(self, dir_name):
		displayText = "Press space, raise your left toe while your heel is on the ground, and hold for 5 seconds"
		self.captureHold(dir_name, "LEFT-TOE-UP", displayText, 5)

	def captureLEFT_TOE_TAP(self, dir_name):
		displayText = "Press SPACE, tap your left toe once and then press SPACE as soon as you are done"
		self.captureExplicit(dir_name, "LEFT-TOE-TAP", displayText)

	def captureLEFT_HEEL_TAP(self, dir_name):
		displayText = "Press SPACE, tap your left heel once and then press SPACE as soon as you are done"
		self.captureExplicit(dir_name, "LEFT-HEEL-TAP", displayText)

	def captureLEFT_HEEL_RAISE(self, dir_name):
		displayText = "Press SPACE, raise your left heel, and hold for five seconds"
		self.captureHold(dir_name, "LEFT-HEEL-RAISE", displayText, 5)

	def captureLEFT_FOOT_FLICKLEFT(self, dir_name):
		displayText = "Press SPACE, flick your left foot to the left, and then press SPACE as soon as you are done"
		self.captureExplicit(dir_name, "LEFT-FOOT-FLICKLEFT", displayText)

	def captureLEFT_FOOT_FLICKRIGHT(self, dir_name):
		displayText = "Press SPACE, flick your left foot to the right, and then press SPACE as soon as you are done"
		self.captureExplicit(dir_name, "LEFT-FOOT-FLICKRIGHT", displayText)

	def captureLEFT_FOOT_SPINCW(self, dir_name):
		displayText = "Press SPACE, spin your left foot clockwise, and then press SPACE as soon as you are done"
		self.captureExplicit(dir_name, "LEFT-FOOT-SPINCW", displayText)

	def captureLEFT_FOOT_SPINACW(self, dir_name):
		displayText = "Press SPACE, spin your left foot anticlockwise, and then press SPACE as soon as you are done"
		self.captureExplicit(dir_name, "LEFT-FOOT-SPINACW", displayText)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Capture traing data for smartshoes")
	parser.add_argument("DIR", action = "store", type = str, help = "The directory to store captured data in")
	parser.add_argument("-n", action = "store", default = 5, type = int, dest = "num_trials", help = "The Number of times to capture data for each gesture (default : 10)")
	parser.add_argument("-s", action = "store", default = "/dev/input/smartshoes", type = str, dest = "streamFile", help = "The Name of the stream to read input from (default: /dev/input/smartshoes)")
	inputArgs = parser.parse_args()
	main(inputArgs)
