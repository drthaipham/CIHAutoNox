# CIHAutoNox

Tested on Kodi 16.2

This is a modified version of scope nox by funkd.. which is a modified version of AeonNox by BigNoid.
Features:

    - Can tag files with correct aspect ratio and audio codec: Atmos, DTS-X. in the .nfo file, add a genre containing:
        atmos, dts-x, AR133, AR137, AR166, AR178, AR185, AR220, AR235, AR240, AR255, AR276 (** NOT CASE SENSITIVE **)
        i.e. <genre>Dolby Atmos</genre>, or <genre>atmos AR235</genre>, or <genre>Atmos DTS-X</genre><genre>AR235</genre>
    - Mask (black out) areas outside of the specified aspect ratio.
    - Place the OSD and the Seekbar at the top and bottom of the screen
    - Automatically detect hardcoded black bars and calculate the aspect ratio of the playing video.
    - Can Manually specify the aspect ratio of the playing video.
    - Aspect ratio supported: 2.35, 2.0, 1.85, 16:9, 1.33. 
    **** Requires Kodi addon KodiCallback for autoaspect ratio detection ***
    - Can be used to control/recall projector settings specific to the AR of the playing video.

Idealy used for CIH zoom setups. 

Using the normal Kodi skins in this cases causes part of the skin to spill outside the scope frame onto walls.

This version of the skin contains all the GUI within an 800/820 pixel height. 


**************************
** Installation and Use **
**************************

1) Download the zip files to the Kodi device.<br>
    a) script.cihautonox.tools.zip<br>
    b) skin.cihautonox.1.0.zip <br>
<br>
2) Goto Addons, "Install from Zip" and install the two zip files<br>
<br>
3) Install the Kodi Callbacks addon. http://kodi.wiki/view/Add-on:Kodi_Callbacks<br>
    Available through the official repo (isengard forward) as of 22-04-2016<br>
<br>
4) Configuring KodiCallBacks:<br>
    Task 1: builtin - RunScript(script.cihautonox.tools,autoaspect)<br>
    Task 2: buitin - RunScript(script.cihautonox.tools,133stop)<br>
    Event 1: On PlaybackStarted - Task1<br>
    Event 2: On PlaybackStopped - Task2 (so we can remove the 1.33 side masks for the gui)<br>
<br>
5) Play a file and (hopefully) watch the magic happens.

***********************************************************************
** changing the projector zoom settings with the aspect ratio change **
***********************************************************************
The cool thing would be to control the projector zoom setting based on the video file.
the JVC-RS400 projector has lens memory settings. I just set up the memory slots for
2.35, 2.0, 1.85, 16:9, 1.33. 
These lens memory settings can be recalled via ip control. Unfortunately, IP control 
for the RS400 can only take request from one source at a time. i.e., kodi, and another
remote control app cannot both control the RS400.

The solution is to use a gateway. I just use the simplecontrol app. I have activities set
up to recall the various zoom settings. (Named Mask235, Mask200, Mask185, Mask169 in my case.)
Then on changing the aspect ratio on the skin, the script also tells simple control to run
the associated activity.

********************************
** Changing the Masking sizes **
********************************
custom_1131_ScopeBars133.xml - contains the mask for 133 aspect ratio<br>
custom_1132_ScopeBars235.xml - contains the mask for 235 aspect ratio<br>
custom_1133_ScopeBars200.xml - contains the mask for 200 aspect ratio<br>
custom_1134_ScopeBars185.xml - contains the mask for 185 aspect ratio.<br>
16:9 obviously does not need masking as it is the whole panel size.<br>

*************************
** Other files of note **
*************************
VideoOSD.xml - contains the OSD and aspect ratio changing buttons.
DiaglogSeekBar.xml - contains the code for the seek bar in the bottom of the screen.


