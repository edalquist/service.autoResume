'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import xbmc
import xbmcaddon
from time import sleep


ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
FOLDER = ADDON.getSetting('autoresume.save.folder').encode('utf-8', 'ignore')
FREQUENCY = int(ADDON.getSetting('autoresume.frequency'))
PATH = os.path.join(FOLDER, 'autoresume.txt')
PATH_TMP = os.path.join(FOLDER, 'autoresume.tmp')

def resume():
  for x in range(0,120):
    if os.path.exists(FOLDER):
      if os.path.exists(PATH):
        # Read from autoresume.txt.
        f = open(PATH, 'r')
        mediaFile = f.readline().rstrip('\n')
        position = float(f.readline())
        f.close()
        # Play file.
        xbmc.Player().play(mediaFile)
        while (not xbmc.Player().isPlaying()):
          sleep(0.5)
        sleep(1)
        # Seek to last recorded position.
        xbmc.Player().seekTime(position)
        sleep(1)
        # Make sure it actually got there.
        if abs(position - xbmc.Player().getTime()) > 30:
          xbmc.Player().seekTime(position)
      break
    else:
      # If the folder didn't exist maybe we need to wait longer for the drive to be mounted.
      sleep(5)

def recordPosition(prev_state):
  (prev_media_file, prev_position, prev_playing, count) = prev_state
  if xbmc.Player().isPlaying():
    media_file = xbmc.Player().getPlayingFile()
    position = xbmc.Player().getTime()
    log("Currently playing: %s" % media_file)
    # Write info to temp file, then actual file, try to make this idempotent
    if not xbmc.abortRequested and (not prev_playing or media_file != prev_media_file or position != prev_position):
      log("Writing %s" % PATH_TMP)
      f = open(PATH_TMP, 'w', 0)
      f.write("%s\n%f" % (media_file, position))
      f.close()
      log("Renaming %s to %s" % (PATH_TMP, PATH))
      os.rename(PATH_TMP, PATH)
    return (media_file, position, True, count + 1 if prev_playing else 1)
  else:
    log("Nothing currently playing")
    if not prev_playing and count > 2 and os.path.exists(PATH) and not xbmc.abortRequested:
      log("Deleting %s" % PATH)
      os.remove(PATH)
    return (None, None, False, count + 1 if not prev_playing else 1)

def log(msg):
  xbmc.log("%s: %s" % (ADDON_ID, msg), xbmc.LOGDEBUG)


if __name__ == "__main__":
  log("Resuming")
  resume()
  log("Start recording position")
  state = (None, None, False, 0)
  while (not xbmc.abortRequested):
    state = recordPosition(state)
    # TODO don't just sleep, causes shutdown delays
    sleep(FREQUENCY)
