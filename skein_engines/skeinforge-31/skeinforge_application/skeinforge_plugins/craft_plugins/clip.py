"""
This page is in the table of contents.
Clip clips the ends of loops to prevent bumps from forming.

The clip manual page is at:
http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Clip

==Operation==
The default 'Activate Clip' checkbox is on.  When it is on, the functions described below will work, when it is off, the functions will not be called.

==Settings==
===Clip Over Perimeter Width===
Default is 0.2.

Defines the ratio of the amount each end of the loop is clipped over the perimeter width.  The total gap will therefore be twice the clip.  If the ratio is too high loops will have a gap, if the ratio is too low there will be a bulge at the loop ends.

===Maximum Connection Distance Over Perimeter Width===
Default is ten.

Defines the ratio of the maximum connection distance between loops over the perimeter width.  If the ratio is zero, nothing will be done.  If it is ratio greater than zero, clip will connect nearby loops, combining them into a spiral.  For loop connection, nearby means that the distance between a pair of loops is smaller or equal to the maximum connection distance.

==Examples==
The following examples clip the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and clip.py.


> python clip.py
This brings up the clip dialog.


> python clip.py Screw Holder Bottom.stl
The clip tool is parsing the file:
Screw Holder Bottom.stl
..
The clip tool has created the file:
.. Screw Holder Bottom_clip.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import clip
>>> clip.main()
This brings up the clip dialog.


>>> clip.writeOutput('Screw Holder Bottom.stl')
The clip tool is parsing the file:
Screw Holder Bottom.stl
..
The clip tool has created the file:
.. Screw Holder Bottom_clip.gcode

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import intercircle
from fabmetheus_utilities import settings
from fabmetheus_utilities.fabmetheus_tools import fabmetheus_interpret
from skeinforge_application.skeinforge_utilities import skeinforge_craft
from skeinforge_application.skeinforge_utilities import skeinforge_polyfile
from skeinforge_application.skeinforge_utilities import skeinforge_profile
import math
import sys


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__date__ = '$Date: 2008/21/04 $'
__license__ = 'GPL 3.0'


def getCraftedText( fileName, text, clipRepository = None ):
	"Clip a gcode linear move file or text."
	return getCraftedTextFromText( gcodec.getTextIfEmpty( fileName, text ), clipRepository )

def getCraftedTextFromText( gcodeText, clipRepository = None ):
	"Clip a gcode linear move text."
	if gcodec.isProcedureDoneOrFileIsEmpty( gcodeText, 'clip'):
		return gcodeText
	if clipRepository == None:
		clipRepository = settings.getReadRepository( ClipRepository() )
	if not clipRepository.activateClip.value:
		return gcodeText
	return ClipSkein().getCraftedGcode( clipRepository, gcodeText )

def getNewRepository():
	"Get the repository constructor."
	return ClipRepository()

def writeOutput( fileName = ''):
	"Clip a gcode linear move file.  Chain clip the gcode if it is not already clipped.  If no fileName is specified, clip the first unmodified gcode file in this folder."
	fileName = fabmetheus_interpret.getFirstTranslatorFileNameUnmodified(fileName)
	if fileName != '':
		skeinforge_craft.writeChainTextWithNounMessage( fileName, 'clip')


class ClipRepository:
	"A class to handle the clip settings."
	def __init__(self):
		"Set the default settings, execute title & settings fileName."
		skeinforge_profile.addListsToCraftTypeRepository('skeinforge_application.skeinforge_plugins.craft_plugins.clip.html', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( fabmetheus_interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Clip', self, '')
		self.openWikiManualHelpPage = settings.HelpPage().getOpenFromAbsolute('http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Clip')
		self.activateClip = settings.BooleanSetting().getFromValue('Activate Clip', self, True )
		self.clipOverPerimeterWidth = settings.FloatSpin().getFromValue( 0.1, 'Clip Over Perimeter Width (ratio):', self, 0.8, 0.5 )
		self.maximumConnectionDistanceOverPerimeterWidth = settings.FloatSpin().getFromValue( 1.0, 'Maximum Connection Distance Over Perimeter Width (ratio):', self, 20.0, 10.0 )
		self.executeTitle = 'Clip'

	def execute(self):
		"Clip button has been clicked."
		fileNames = skeinforge_polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, fabmetheus_interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput(fileName)


class ClipSkein:
	"A class to clip a skein of extrusions."
	def __init__(self):
		self.distanceFeedRate = gcodec.DistanceFeedRate()
		self.extruderActive = False
		self.feedRateMinute = None
		self.isLoopPerimeter = False
		self.loopPath = None
		self.lineIndex = 0
		self.oldLocation = None
		self.oldWiddershins = None
		self.travelFeedRatePerMinute = None

	def addGcodeFromThreadZ( self, thread, z ):
		"Add a gcode thread to the output."
		if len(thread) > 0:
			self.distanceFeedRate.addGcodeMovementZWithFeedRate( self.travelFeedRatePerMinute, thread[0], z )
		else:
			print( "zero length vertex positions array which was skipped over, this should never happen" )
		if len(thread) < 2:
			print( "thread of only one point in clip, this should never happen" )
			print(thread)
			return
		self.distanceFeedRate.addLine('M101')
		for point in thread[1 :]:
			self.distanceFeedRate.addGcodeMovementZWithFeedRate( self.feedRateMinute, point, z )

	def addSegmentToPixelTables( self, location, maskPixelTable, oldLocation ):
		"Add the segment to the layer and mask table."
#		segmentTable = {}
		euclidean.addValueSegmentToPixelTable( oldLocation.dropAxis(2), location.dropAxis(2), self.layerPixelTable, None, self.layerPixelWidth )
#		euclidean.addValueSegmentToPixelTable( oldLocation.dropAxis(2), location.dropAxis(2), segmentTable, None, self.layerPixelWidth )
#		euclidean.addPixelTableToPixelTable( segmentTable, self.layerPixelTable )
#		euclidean.addPixelTableToPixelTable( segmentTable, maskPixelTable )
#		self.maskPixelTableTable[ location ] = maskPixelTable
#		self.maskPixelTableTable[ oldLocation ] = maskPixelTable

	def addTailoredLoopPath(self, line):
		"Add a clipped loop path."
		if self.clipLength > 0.0:
			removeTable = {}
			euclidean.addLoopToPixelTable( self.loopPath.path, removeTable, self.layerPixelWidth )
			euclidean.removePixelTableFromPixelTable( removeTable, self.layerPixelTable )
			self.loopPath.path = euclidean.getClippedLoopPath( self.clipLength, self.loopPath.path )
			self.loopPath.path = euclidean.getSimplifiedPath( self.loopPath.path, self.perimeterWidth )
			euclidean.addLoopToPixelTable( self.loopPath.path, self.layerPixelTable, self.layerPixelWidth )
		if self.oldWiddershins == None:
			self.addGcodeFromThreadZ( self.loopPath.path, self.loopPath.z )
		else:
			if self.oldWiddershins != euclidean.isWiddershins( self.loopPath.path ):
				self.loopPath.path.reverse()
#			self.addGcodeFromThreadZ( self.loopPath.path, self.loopPath.z )
			for point in self.loopPath.path:
				self.distanceFeedRate.addGcodeMovementZWithFeedRate( self.feedRateMinute, point, self.loopPath.z )
		if self.getNextThreadIsACloseLoop( self.loopPath.path ) and self.maximumConnectionDistance > 0.0:
			self.oldWiddershins = euclidean.isWiddershins( self.loopPath.path )
		else:
			self.oldWiddershins = None
			self.distanceFeedRate.addLine(line)
		self.loopPath = None

	def getConnectionIsCloseWithoutOverlap( self, location, path ):
		"Determine if the connection is close enough and does not overlap another thread."
		if len(path) < 1:
			return False
		locationComplex = location.dropAxis(2)
		segment = locationComplex - path[-1]
		segmentLength = abs( segment )
		if segmentLength <= 0.0:
			return True
		if segmentLength > self.maximumConnectionDistance:
			return False
		segment /= segmentLength
		distance = self.connectingStepLength
		segmentEndLength = segmentLength - self.connectingStepLength
		while distance < segmentEndLength:
			alongPoint = distance * segment + path[-1]
			if not euclidean.getIsInFilledRegion( self.boundaryLoops, alongPoint ):
				return False
			distance += self.connectingStepLength
#		removedLayerPixelTable = self.layerPixelTable.copy()
#		if self.oldLocation in self.maskPixelTableTable:
#			euclidean.removePixelTableFromPixelTable( self.maskPixelTableTable[ self.oldLocation ], removedLayerPixelTable )
#		euclidean.addPathToPixelTable( path[ : - 2 ], removedLayerPixelTable, None, self.layerPixelWidth )
		segmentTable = {}
		euclidean.addSegmentToPixelTable( path[-1], locationComplex, segmentTable, 2.0, 2.0, self.layerPixelWidth )
#		euclidean.addValueSegmentToPixelTable( path[-1], locationComplex, segmentTable, None, self.layerPixelWidth )
#		euclidean.addValueSegmentToPixelTable( path[-1], locationComplex, segmentTable, None, self.layerPixelWidth )
#		maskPixelTable = {}
#		if location in self.maskPixelTableTable:
#			maskPixelTable = self.maskPixelTableTable[ location ]
		if euclidean.isPixelTableIntersecting( self.layerPixelTable, segmentTable, {} ):
#		if euclidean.isPixelTableIntersecting( removedLayerPixelTable, segmentTable, {} ):
			return False
		euclidean.addValueSegmentToPixelTable( path[-1], locationComplex, self.layerPixelTable, None, self.layerPixelWidth )
#		euclidean.addPixelTableToPixelTable( segmentTable, self.layerPixelTable )
		return True

	def getCraftedGcode( self, clipRepository, gcodeText ):
		"Parse gcode text and store the clip gcode."
		self.lines = gcodec.getTextLines(gcodeText)
		self.parseInitialization( clipRepository )
		for self.lineIndex in xrange( self.lineIndex, len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
			self.parseLine(line)
		return self.distanceFeedRate.output.getvalue()

	def getNextThreadIsACloseLoop( self, path ):
		"Determine if the next thread is a loop."
		if self.oldLocation == None:
			return False
		isLoop = False
		location = self.oldLocation
		for afterIndex in xrange( self.lineIndex + 1, len( self.lines ) ):
			line = self.lines[ afterIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
			firstWord = gcodec.getFirstWord(splitLine)
			if firstWord == '(<loop>' or firstWord == '(<perimeter>':
				isLoop = True
			elif firstWord == 'G1':
				location = gcodec.getLocationFromSplitLine(self.oldLocation, splitLine)
			elif firstWord == 'M101':
				if not isLoop:
					return False
				return self.getConnectionIsCloseWithoutOverlap( location, path )
			elif firstWord == '(<layer>':
				return False
		return False

	def isNextExtruderOn(self):
		"Determine if there is an extruder on command before a move command."
		for afterIndex in xrange( self.lineIndex + 1, len( self.lines ) ):
			line = self.lines[ afterIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
			firstWord = gcodec.getFirstWord(splitLine)
			if firstWord == 'G1' or firstWord == 'M103':
				return False
			elif firstWord == 'M101':
				return True
		return False

	def linearMove( self, splitLine ):
		"Add to loop path if this is a loop or path."
		location = gcodec.getLocationFromSplitLine(self.oldLocation, splitLine)
		self.feedRateMinute = gcodec.getFeedRateMinute( self.feedRateMinute, splitLine )
		if self.isLoopPerimeter:
			if self.isNextExtruderOn():
				self.loopPath = euclidean.PathZ(location.z)
		if self.loopPath == None:
			if self.extruderActive:
				self.oldWiddershins = None
		else:
			self.loopPath.path.append( location.dropAxis(2) )
		self.oldLocation = location

	def parseInitialization( self, clipRepository ):
		"Parse gcode initialization and store the parameters."
		for self.lineIndex in xrange( len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
			firstWord = gcodec.getFirstWord(splitLine)
			self.distanceFeedRate.parseSplitLine( firstWord, splitLine )
			if firstWord == '(</extruderInitialization>)':
				self.distanceFeedRate.addLine('(<procedureDone> clip </procedureDone>)')
				return
			elif firstWord == '(<perimeterWidth>':
				self.perimeterWidth = float(splitLine[1])
				absolutePerimeterWidth = abs( self.perimeterWidth )
				self.clipLength = clipRepository.clipOverPerimeterWidth.value * self.perimeterWidth
				self.connectingStepLength = 0.5 * absolutePerimeterWidth
				self.layerPixelWidth = 0.1 * absolutePerimeterWidth
				self.maximumConnectionDistance = clipRepository.maximumConnectionDistanceOverPerimeterWidth.value * absolutePerimeterWidth
			elif firstWord == '(<travelFeedRatePerSecond>':
				self.travelFeedRatePerMinute = 60.0 * float(splitLine[1])
			self.distanceFeedRate.addLine(line)

	def parseLine(self, line):
		"Parse a gcode line and add it to the clip skein."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
		if len(splitLine) < 1:
			return
		firstWord = splitLine[0]
		if firstWord == 'G1':
			self.linearMove(splitLine)
		elif firstWord == 'M101':
			self.extruderActive = True
		elif firstWord == 'M103':
			self.extruderActive = False
			self.isLoopPerimeter = False
			if self.loopPath != None:
				self.addTailoredLoopPath(line)
				return
		elif firstWord == '(<layer>':
			self.setLayerPixelTable()
		if firstWord == '(<loop>' or firstWord == '(<perimeter>':
			self.isLoopPerimeter = True
		if self.loopPath == None:
			self.distanceFeedRate.addLine(line)

	def setLayerPixelTable(self):
		"Set the layer pixel table."
		boundaryLoop = None
		extruderActive = False
		maskPixelTable = {}
		self.boundaryLoops = []
		self.maskPixelTableTable = {}
		self.lastInactiveLocation = None
		self.layerPixelTable = {}
		oldLocation = self.oldLocation
		for afterIndex in xrange( self.lineIndex + 1, len( self.lines ) ):
			line = self.lines[ afterIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
			firstWord = gcodec.getFirstWord(splitLine)
			if firstWord == 'G1':
				location = gcodec.getLocationFromSplitLine(oldLocation, splitLine)
				if extruderActive and oldLocation != None:
					self.addSegmentToPixelTables( location, maskPixelTable, oldLocation )
				if not extruderActive:
					self.lastInactiveLocation = location
				oldLocation = location
			elif firstWord == 'M101':
				extruderActive = True
			elif firstWord == 'M103':
				if extruderActive and self.lastInactiveLocation != None:
					self.addSegmentToPixelTables( self.lastInactiveLocation, maskPixelTable, oldLocation )
				extruderActive = False
				maskPixelTable = {}
			elif firstWord == '(</boundaryPerimeter>)':
				boundaryLoop = None
			elif firstWord == '(<boundaryPoint>':
				if boundaryLoop == None:
					boundaryLoop = []
					self.boundaryLoops.append( boundaryLoop )
				location = gcodec.getLocationFromSplitLine(None, splitLine)
				boundaryLoop.append( location.dropAxis(2) )
			elif firstWord == '(</layer>)':
				return

def main():
	"Display the clip dialog."
	if len( sys.argv ) > 1:
		writeOutput(' '.join( sys.argv[1 :] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
