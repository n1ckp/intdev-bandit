#Allows for relative import
import sys, os, argparse, random, uuid, time
import pygame
sys.path.append(os.path.abspath("../"))

from utils.streamUtils.StreamRead import StreamRead

class main():

	def __init__(self, inputArgs):
		pygame.init()
	 	size = width, height = 800, 800
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

		self.gesture_classes = {"REST" : self.captureREST, "LEFT-FOOT-STAMP" : self.captureLEFT_FOOT_STAMP, "LEFT-FRONT-UP" : self.captureLEFT_FRONT_UP}
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
		self.textToScreen("Thankyou, please rest your feet and wait for the next test")
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

	#Capture resting gesture
	def captureREST(self, dir_name):
		self.textToScreen("Please press SPACE and then keep your feet at rest for the next 5 seconds")
		ready = False

		#wait for user to being test
		while not ready:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN :
					if event.key == pygame.K_SPACE :
						ready = True

		self.textToScreen("Please wait 5 seconds")

		#Capture for 1 second 5 times
		for i in xrange(0, 5):
			output_file = self.makeFile(dir_name, "REST")
			self.stream.emptyStreamBuffer()
			stop = time.time() + 1
			while time.time() < stop:
				records = self.stream.readFromStream()
				for record in records:
					self.writeData(output_file, record)

		
	# Capture left foot stamp
	def captureLEFT_FOOT_STAMP(self, dir_name):
		self.textToScreen("Please tap SPACE, Stamp your left foot and then tap SPACE as soon as you are done")

		output_file = self.makeFile(dir_name, "LEFT-FOOT-STAMP")

		ready = False
		done = False

		#Wait for user to begin test
		while not ready:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN :
					if event.key == pygame.K_SPACE :
						ready = True

		self.stream.emptyStreamBuffer()
		#read data until space is pressed
		while not done:
			records = self.stream.readFromStream()
			for record in records:
				self.writeData(output_file, record)

			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN :
					if event.key == pygame.K_SPACE :
						done = True

	#Capture toe lifted
	def captureLEFT_FRONT_UP(self, dir_name):
		self.textToScreen("Please elevate the front of your left foot,")
		self.textToScreen("press SPACE and maintain the position for 5 seconds", y_pos=40)
		ready = False

		#wait for user to being test
		while not ready:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN :
					if event.key == pygame.K_SPACE :
						ready = True

		self.textToScreen("Please wait 5 seconds")

		#Capture for 1 second 5 times
		for i in xrange(0, 5):
			output_file = self.makeFile(dir_name, "LEFT-FRONT-UP")
			self.stream.emptyStreamBuffer()
			stop = time.time() + 1
			while time.time() < stop:
				records = self.stream.readFromStream()
				for record in records:
					self.writeData(output_file, record)




if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Capture traing data for smartshoes")
	parser.add_argument("DIR", action = "store", type = str, help = "The directory to store captured data in")
	parser.add_argument("-n", action = "store", default = 5, type = int, dest = "num_trials", help = "The Number of times to capture data for each gesture (default : 10)")
	parser.add_argument("-s", action = "store", default = "/dev/input/smartshoes", type = str, dest = "streamFile", help = "The Name of the stream to read input from (default: /dev/input/smartshoes)")
	inputArgs = parser.parse_args()
	main(inputArgs)

	
	
