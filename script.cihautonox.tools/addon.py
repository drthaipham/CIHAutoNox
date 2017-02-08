import json
import urllib
import urllib2
import sys
import xbmc
import xbmcaddon
import xbmcgui
import os.path

addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
capture     = xbmc.RenderCapture()
myplayer    = xbmc.Player()

# interface to run activity for simple control
SCCommand = 'http://<your simplecontrol hub ip address>:47147/api/v1/runactivity'
SCActivity_widescreen = "<your simple control activity UUID>"
SCActivity_20screen   = "<your simple control activity UUID>"
SCActivity_185screen  = "<your simple control activity UUID>"
SCActivity_169screen  = "<your simple control activity UUID>"
SCActivity_133screen  = "<your simple control activity UUID>"
SCActivity_lowlights  = "<your simple control activity UUID>"
SCActivity_movielights = "<your simple control activity UUID>"

# capture Width & Height
# 1080p 1920x1080 - 40x40pixel per captured pixel. 1920x1080 -> 48x27
# 1038:1.85  960:2.0  817:2.35
# each captured line represents 40 lines in the encoded image. aspect
# ratio changes are in multiples of 40s
CaptureWidth = 48
CaptureHeight = 27


# subtitle vertical positions for aspect ratio
Sub235 = 860
Sub200 = 1000
Sub185 = 1040
Sub169 = 1080
Sub133 = 1080



###########
#
# SCRunActivity
#   sends a json rpc to simple control to change projector zoom / lenshift /masking
#   In simplecontrol, set an activity to recall the projector lens memory
#   get the activity uuid by going to:
#   http://<simple control hub ip address>:47147/api/v1/activities
#   then copy the UUID to the above variable. i.e. SCActivity_169 screen
#
###########
def SCRunActivity (activity):
    return
    temp = '{"activity_uuid" : "' + activity + '"}'
    urllib.urlopen (SCCommand, temp)

###########
#
# PARdecrease
# PARincrease
# PARReset
#    needs custom Kodi. These ActionIDs are not in the standard Kodi yet.
#    will not break the script if it's not used.
#
###########
PARSteps = 11
def PARdecrease ():
    for i in range (1, PARSteps):
        xbmc.executebuiltin ('XBMC.Action(DecreasePARSilent)')

def PARincrease ():
    xbmc.executebuiltin('Skin.setbool (osdstretched)')
    for i in range (1, PARSteps):
        xbmc.executebuiltin ('XBMC.Action(IncreasePARSilent)')

def PARReset ():
    xbmc.executebuiltin ('XBMC.Action(ResetPAR)')
    xbmc.executebuiltin('Skin.reset (osdstretched)')

###########
#
# SubtitleVshiftSet
#   Set absolute subtitle conditions
#   works best with subtitle align manual
#
# does not work... likely problem with how kodi renders subtitles
###########

def SubtitleVshiftSet (_count):
    return
    xbmc.executebuiltin ('XBMC.Action(ResetSubtitleVshift)')
    for i in range (1, _count):
        xbmc.executebuiltin ('XBMC.Action(IncreaseSubtitleVshift)')

###########
#
# ARChanges routine
#   notifies the skin CIHAutoNox of the aspect ratio change
###########
def ARClearBooleans ():
    xbmc.executebuiltin('Skin.reset (osd133)')
    xbmc.executebuiltin('Skin.reset (osd169)')
    xbmc.executebuiltin('Skin.reset (osd185)')
    xbmc.executebuiltin('Skin.reset (osd200)')
    xbmc.executebuiltin('Skin.reset (osd235)')

def ARChange133():
    SCRunActivity (SCActivity_133screen)
    SubtitleVshiftSet (Sub133)
    ARClearBooleans()
    xbmc.executebuiltin('Skin.setbool (osd133)')

def ARChange169():
    SCRunActivity (SCActivity_169screen)
    SubtitleVshiftSet (Sub169)
    ARClearBooleans ()
    xbmc.executebuiltin('Skin.setbool (osd169)')

def ARChange185():
    SCRunActivity (SCActivity_185screen)
    SubtitleVshiftSet (Sub185)
    ARClearBooleans()
    xbmc.executebuiltin('Skin.setbool (osd185)')

def ARChange200():
    SCRunActivity (SCActivity_20screen)
    SubtitleVshiftSet (Sub200)
    ARClearBooleans()
    xbmc.executebuiltin('Skin.setbool (osd200)')


def ARChange235():
    SCRunActivity (SCActivity_widescreen)
    SubtitleVshiftSet (Sub235)
    ARClearBooleans ()
    xbmc.executebuiltin('Skin.setbool (osd235)')

##############
#
# CaptureFrame
#
# Capture a frame into variable "capture"
# global variable - capture, CaptureWidth, CaptureHeight
# returns - image byte array
#############
def CaptureFrame ():
    capture.capture(CaptureWidth,CaptureHeight, xbmc.CAPTURE_FLAG_CONTINUOUS)
        
    while (capture.getCaptureState() != xbmc.CAPTURE_STATE_DONE):
        capture.waitForCaptureStateChangeEvent ()
        
        if (capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE):
            capturedImage = capture.getImage()
            return capturedImage

def CaptureFrame_new ():
    capture.Capture (CaptureWidth, CaptureHeight)
    capturedImage = capture.getImage (1000)
    return capturedImage

##############
#
# LineColorLessThan
#    _bArray: byte Array that contains the data we want to test
#    _lineStart: where to start testing
#    _lineCount: how many lines to test
#    _threshold: value to determine testing
# returns: True False
###############
def LineColorLessThan (_bArray, _lineStart, _lineCount, _threshold):
    __sliceStart = _lineStart * CaptureWidth * 4
    __sliceEnd = (_lineStart + _lineCount) * CaptureWidth * 4
    
    # zero out the alpha channel
    i = __sliceStart + 3
    while (i < __sliceEnd):
        _bArray[i] &= 0x00
        i += 4
    
    __imageLine = _bArray[__sliceStart:__sliceEnd]
    __result = all([v < _threshold for v in __imageLine])
    return __result

###############
#
# GetAspectRatioFromFrame
#   - returns Aspect ratio * 100 (i.e. 2.35 = 235)
#   Detects hardcoded black bars
###############
def GetAspectRatioFromFrame ():
    __aspectratio = int( (capture.getAspectRatio() + 0.005) * 100 )
    __threshold = 25
    
    # Analyze the frame only if the ratio is 16:9. 2.35 ratio files
    # would not have black bars hardcoded.
    if 140 < __aspectratio < 180 :
        # screen capture and test for an image that is not dark in the 2.40
        # aspect ratio area. keep on capturing images until captured image
        # is not dark
        while (True):
            __myimage = CaptureFrame()
            __middleScreenDark = LineColorLessThan (__myimage, 4, 1, __threshold)
            if __middleScreenDark == False:
                xbmc.sleep (200)
                break
            else:
                xbmc.sleep (100)

        # Capture another frame. after we have waited for transitions
        __myimage = CaptureFrame()
        __imageLine0Dim = LineColorLessThan (__myimage, 0, 1, __threshold) # line 0, top of image
        __imageLine1Dim = LineColorLessThan (__myimage, 1, 2, __threshold) # really line 1 & 2
        
        if (__imageLine1Dim == True):
            __aspectratio = 235
        elif (__imageLine0Dim == True and __imageLine1Dim == False):
            __aspectratio = 185

    return __aspectratio

###############
#
# AutoaspectChange
#   must be called by kodi on playback start
#   the easiest way is to use the kodi addon: KodiCallback and set Task 1 to:
#   task: builtin
#   kodi builtin function: RunScript(script.cihautonox.tools,autoaspect)
#   then set Event 1: on Playback started
#            task for Event 1: Task 1
#
###############
def AutoaspectChange ():

    aspectratio = GetAspectRatioFromFrame ()
    PARReset()
    
    # 16:9 screen
    if (150 <= aspectratio <= 180):
        ARChange169()
    
    # 1.33 screen
    elif (130 <= aspectratio <= 140):
        ARChange133()
    
    # 1.85 screen
    elif (181 <= aspectratio <= 189):
        ARChange185()
    
    # 2.0 Screen
    elif (190 <= aspectratio <= 210):
        ARChange200()
    
    # 2.35 Screen
    elif (aspectratio > 210):
        ARChange235()

###############
#
# AutoStretch
#   stretch 1:33 -> no stretch
#   stretch      -> 2.0
#   No stretch 2.35 and up
#   same use as above. Could set this as task 2
#
#   *** Does not work in stock Kodi. I am awaiting my pull request to be merged into kodi ***
###############
def AutoStretch ():
    
    aspectratio = GetAspectRatioFromFrame ()
    PARReset()
    
    # 1.33 screen no stretch
    if (130 <= aspectratio <= 140):
        ARChange133()
    
    #stretch 16:9, 1.85:1 to 2.0
    elif ( 150 <= aspectratio <= 189):
        ARChange200 ()
        PARincrease()
    
    #stretch 2.0 to 2.35
    elif ( 190 <= aspectratio <= 210):
        ARChange235 ()
        PARincrease ()

    # 2.35 screen no stretch
    elif (aspectratio >210):
        ARChange235 ()


######################################
######################################

# Set AspectRatio masking on
xbmc.executebuiltin('skin.reset (scopemask)')
xbmc.executebuiltin('Skin.setbool (ARmask)')

#####################
# Testing
#####################

if sys.argv[1] == 'test':
    
    aspectratio = GetAspectRatioFromFrame ()
    aspectratio2 = int ((capture.getAspectRatio () + 0.005) * 100)

    _info = xbmc.getInfoLabel('Player.Process(VideoDAR)')
    _info2 = xbmc.getInfoLabel('Player.Process(videoheight)')
    WIN = xbmcgui.Window(10000)
    line1 = 'Calculated Aspect Ratio = ' + str(aspectratio)
    line2 = 'Player Aspect Ratio = ' + str(aspectratio2)
    line3 = ' '
    xbmcgui.Dialog().ok(addonname,line1, line2, line3)

###################################
# end Testing
###################################


#----------------
# manual scope / masking buttons
#---------------
if sys.argv[1] == 'widescreen':
    ARChange235()

if sys.argv[1] == 'mediumscreen':
    ARChange200()

if sys.argv[1] == '185screen':
    ARChange185()

if sys.argv[1] == 'standardscreen':
    ARChange169()


#----------------
# autoaspect ratio change
#-----------------

if sys.argv[1] == 'autoaspect':
    AutoaspectChange()


if sys.argv[1] == 'autostretch':
    AutoStretch()


#----------------
# shrink
#   unstretch video if it has been stretched.
#-----------------
if sys.argv[1] == 'shrink':
    AutoaspectChange()

#----------------
# stretch
#-----------------
if sys.argv[1] == 'stretch':
    aspectratio = GetAspectRatioFromFrame ()
    

    PARReset()
    
    #stretch 133 to 16:9
    if (130 <= aspectratio <= 140):
        ARChange169()
        PARincrease()
    
    #stretch 16:9, 1.85:1 to 2.0
    elif ( 150 <= aspectratio <= 189):
        ARChange200 ()
        PARincrease()

    #stretch 2.0 to 2.35
    elif ( 190 <= aspectratio <= 210):
        ARChange235 ()
        PARincrease ()

#---------------
# AR133Stops
#   if playing aspectratio 133, and stops, opens mask up to 169
#   if this is not done, the aspect ratio will be masked at 1.33
#---------------
if sys.argv[1] == '133Stop':
    aspectratio = GetAspectRatioFromFrame ()
    if (130 <= aspectratio <= 140):
        ARChange169()

