# 14th December 2021
# PARAMETERS:
#	$1 = X-axis width
#	$2 = Y-axis height
#	$3 = redline values - if the read values exceed this, redline is recalculated and colouring is adjusted accordingly.
#	$4 = file containing values (linefeed separated)

'''WHAT'S NEXT?'''

import subprocess
import os
import time				# Required to introduce sleep inbetween redraws (initially for testing, can be removed)
import math				# Required for sine function (used in RGB calculations)
from sys import argv
scriptName, ARGdisplayWidth, ARGdisplayHeight, ARGredLine, ARGinputFile = argv

inputFile = ARGinputFile
inputFile_open=open(inputFile, 'r', buffering = 16384)

def process_width(vertCount):
	global maxValue, lineValue, vRatio, valueList, lastPrint				# If accessing global variables I have to do this
	piRatio = 3.14159265 / 180
	'''The purpose of lastPrint is to keep track of when the last time the reverse video control sequence was used.'''
	'''This is in the interests of efficiency, i.e. there's no point in sending another code sequence if it's still active.'''
	'''Additionally, it's necessary to determine when to send the appropriate 'off' signals too.'''
	lastPrint = False

	'''Calculate the relative row value the read value has to exceed to qualify for printing in column'''
	vertRow = int(maxValue / displayHeight * vertCount)
	'''Determine the RGB values for a row'''
	'''In the formula: int(abs(255 * math.sin((O + (A / redLine * vertRow)) * piRatio)))'''
	'''255 * (formula): formula results in a fractional value between 0 and 1, hence any number between 0 and 255.'''

	'''The value between 0 and 1 is achieved through the maths sine function'''   # I think this is wrong - review....
	r = int(abs(1 * math.sin((0+ (90 / redLine * vertRow)) * piRatio)))
#	r = 0
	g = int(abs(255 * math.sin(((90 / redLine * vertRow)) * piRatio)))
#	g = 255

	b = 0
#	b = int(abs(   10 + 10 * math.sin(( (90 / redLine * vertRow)) * piRatio)   ))

	listFollowerWidth = listFollower
	count = 0
	lineValue = 0
	while count < displayWidth:
#		r = int(abs(255 * math.sin((count+vertCount+valuesRead*5+0 + (90 / redLine * vertRow)) * piRatio)))
	#	r = 0
#		g = int(abs(255 * math.sin((count+vertCount+valuesRead*5+10 + (180 / redLine * vertRow)) * piRatio)))
	#	g = 255

	#	b = 0
#		b = int(abs(255 * math.sin((count+vertCount+valuesRead*5+20 + (360 / redLine * vertRow)) * piRatio)))
		'''startColumn gradually moves from (displayWidth-1) to <0 and is necessary to determine which display column we start printing'''
		if count >= startColumn:
			if listFollowerWidth <= listLeader:
				value = valueList[listFollowerWidth]
				'''Determine if the new value read (is the displayable area) is the highest'''
				if value > lineValue:
					lineValue = value
				'''Print the column if the [scaled] value is large enough'''
				if value >= vertRow:
					'''looks like there should be something printed in this column (and also determine if codes were sent (or if need to be))'''
					if lastPrint:
#						print(f"{codeRev}{r};{g};{b}m ", end = '')
						print(" ", end = '')
					else:
						print(f"{codeRev}{r};{g};{b}m ", end = '')
						lastPrint = True
				else:
					'''So nothing should be printed here, so send off reverse video codes and turn off the lastPrint indicator'''
					turn_code_off()
				listFollowerWidth += 1
			else:
				'''If we've got to the end of the data then we need to fill in the remaining columns with a blank to ensure the rightmost box column remains in its position'''
				turn_code_off()
		else:
			'''Only print a dot to indicate there's no data yet in a column'''
			print(".", end='')
		count += 1
	return

def turn_code_off():
	global lastPrint
	if lastPrint:
		print(f"{codeRev}{codeOff} ", end = '')
		lastPrint = 0
	else:
		print(" ", end = '')

'''Function to process all rows.'''
def process_height():
	global maxValue, vRatio
	vCount = displayHeight
	print(f"{codeRev}{codeOff}", end = '')
	while vCount > 0:
		vScale = int(vRatio * vCount)
		print(vScaleFormatter.format(vScale) + " \u2502", end = '')
		process_width(vCount)
		print(f"{codeRev}{codeOff}\u2502")
		vCount -= 1
	return

def show_status():
	print(f" Line Value: {lineValue}   Values Read: {valuesRead}   #Values: {len(valueList)}   Follower: {listFollower}   List Leader: {listLeader}   vRatio: {vRatio}   Start column: {startColumn}   Formatter: {vScaleFormatter}  displayWidth: {displayWidth}   ")

def show_values():
	print(f"{valueList}            ")

'''If the maximum value changes and the number of digits in the value increases, it will visually impact the display of the data'''
'''In this circumstance, the displayWidth will be reduced by the difference, and the associated listLeader if necessary'''
# There are some extreme edge cases here - if the difference is so large that it exceeds the displayWindow width - will need to investigate.
# But first lets deal with the basic concept.
def vScale_adjustment(newvScale):
	global redLine, valueList, displayWidth, vScaleFormatter, listLeader, listFollower, startColumn, vScaleLength, newvScaleLength, vScaleLengthDiff
	vScaleLength = len(str(oldMaxValue))
	newvScaleLength = len(str(newvScale))
	vScaleLengthDiff = abs(newvScaleLength - vScaleLength)

#	debug("Before", 40)

# If there's a difference in the vScale lengths then it's time to adjust the display area variables......
	if vScaleLengthDiff or not vScaleFormatter:
		vScaleFormatter = ' {0:' + str(newvScaleLength) + 'd}'
		if newvScaleLength > vScaleLength:
			displayWidth -= vScaleLengthDiff
			if (startColumn - vScaleLengthDiff) < 0:
				listFollower += (vScaleLengthDiff - startColumn)
				if listFollower > listLeader:
					listFollower = listLeader
					print("..............HERE")
			startColumn -= vScaleLengthDiff
		else:
			displayWidth += vScaleLengthDiff
			listFollower -= vScaleLengthDiff
			listLeader -= vScaleLengthDiff
			if listLeader < 0:
				listLeader = listFollower = 0
			if listFollower < 0:
				listFollower = 0
			if len(valueList) <= vScaleLengthDiff:
				del valueList[:(len(valueList) - 1)]
			else:
				del valueList[:vScaleLengthDiff]
		if startColumn < 0:
			startColumn = 0

#	debug("AFTER", 1)

'''This function resets the scaling factor to be 1:1 with the displayHeight'''
def set_maxValue():
	global displayWidth, maxValue, oldMaxValue, vRatio, redLine, vScaleFormatter
	if maxValue < displayHeight:
		maxValue = displayHeight
	vRatio = maxValue / displayHeight
	'''If redLine value increases then keep track to keep values displayed nicely'''
	if maxValue != oldMaxValue:
		vScale_adjustment(maxValue)

def print_header():
	print(" " * len(str(maxValue)), "  \u250c", "\u2500" * displayWidth, "\u2510", sep = '')

def print_footer():
	print(" " * len(str(maxValue)), "  \u2514", "\u2500" * displayWidth, "\u2518", sep = '')

def debug(text, s):
	global vScaleLength, newvScaleLength, vScaleLengthDiff
	print(home, "\n" * 60)
	spacer = '20'
	print(" " * s, text, sep='')
	print("." * s + "lineValue:\t", lineValue,"     ")
	print(" " * s + "valuesRead:\t", valuesRead,"     ")

	print("." * s + "displayWidth:\t", displayWidth,"     ")
	print(" " * s + "redLine:\t", redLine,"     ")
	print("." * s + "maxValue:\t", maxValue,"     ")
	print("." * s + "oldMaxValue:\t", oldMaxValue,"     ")

	print(" " * s + "startColumn:\t", startColumn,"     ")
	print(" " * s + "# VALUES:\t", len(valueList),"     ")
	print("." * s + "listFollower:\t", listFollower,"     ")
	print(" " * s + "listLeader:\t", listLeader,"     ")
	print("." * s + "vScaleFormatter:\t", vScaleFormatter,"     ")
	print(" " * s + "vScaleLength:\t", vScaleLength,"     ")
	print("." * s + "newvScaleLength:\t", newvScaleLength,"     ")
	print(" " * s + "vScaleLengthDiff:\t", vScaleLengthDiff,"     ")


# Main parameter setup
# Main parameter setup
# Main parameter setup
# Main parameter setup
# Main parameter setup
# Main parameter setup
# Main parameter setup
# Main parameter setup
# Main parameter setup
vRatio = 1.0
displayWidth = int(ARGdisplayWidth)
displayHeight = int(ARGdisplayHeight)
redLine = int(ARGredLine) ; vScaleFormatter = ''
maxValue = displayHeight; oldMaxValue = 0
startColumn = displayWidth - 1

# Track list of values
listLeader = listFollower = 0
valueList = []
valuesToRead = True

'''Determine first maximum value to get scale right before we start, the move back to begining of the file'''
firstValueRead = inputFile_open.readline()
if firstValueRead:
	valuesRead = 1
	valueList.append(int(firstValueRead.strip()))
	maxValue = lineValue = int(firstValueRead.strip())
else:
	print(">>>> ABORTING: NO VALUES TO READ <<<<<")
	quit()
# Escape code sequences for printing reverse video and colour
codeRev = "\033[48;2;"
codeOff = "0;0;0m"
r = g = b = 0


'''External system stuff to get control codes to return to the screen home position'''
home = subprocess.check_output('tput home', shell=True, text=True)
os.system('clear')

set_maxValue()
################################################################################################################
################################################################################################################
################################################################################################################
################################################################################################################
################################################################################################################
################################################################################################################
################################################################################################################


'''Main loop - keep going until there's no more data.'''
'''listFollower is index for the beginning of the values list, listLeader is the most recent value read.'''
'''When listFollower has caught up with listLeader (because no more values are being added) we'll have finished.'''
while listFollower <= (listLeader + 1):
	print(home,end='')
#	show_status()
#	show_values()
	'''Reprints header and footer when maxValue value changes.  Technically should do this when it's width'''
	'''changes, but meh...'''
	if maxValue != oldMaxValue:
		print_header()
	else:
		print()

	process_height()
	if maxValue != oldMaxValue:
		print_footer()
		oldMaxValue = maxValue

# Now determine what the next value is going to be (appearing on the rightmost part of the screen)
	if valuesToRead:
		nextValue = inputFile_open.readline()
		'''Increase the number of values read to the values list if the index qty hasn't exceeded qty displayWidth on screen'''
		if nextValue:
			valuesRead += 1
			if listLeader < (displayWidth-1):
				listLeader += 1
			else:
				'''If we're now at the maximum displayable values on screen, lose the earliest one as we'll never need it again.'''
				'''(this helps to keep the values list to index qty displayWidth max rather than an ever increasing number)'''
				valueList.pop(0)
			'''Add the latest value read to the end of the values list.'''
			nextValueInt = int(nextValue.strip())
			valueList.append(nextValueInt)
			'''Check if the most recent value requires changing the vertical scaling ratio.'''
			if nextValueInt > lineValue:
				lineValue = nextValueInt
		else:
			valuesToRead = False
	'''The maximum displayable value is needed to be kept for dynamic scaling, but ensure the minimum value is 1:1 with displayHeight'''
	maxValue = lineValue

	'''When the first value read has scrolled to the leftmost position and there's no more values to read, start increasing listFollower'''
	if startColumn <= 0:
		if not valuesToRead:
			listFollower += 1
	else:
		startColumn -= 1

	set_maxValue()
# redLine value is used for colour calculations
	if maxValue > redLine:
		redLine = maxValue
#	input("> ")
#	time.sleep(0.1)
print()
