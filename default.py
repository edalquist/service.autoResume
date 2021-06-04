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
import time
from time import sleep


ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
FOLDER = ADDON.getSetting('autoresume.save.folder').encode('utf-8', 'ignore')
FREQUENCY = int(ADDON.getSetting('autoresume.frequency'))
PATH = os.path.join(FOLDER, 'autoresume.txt')
PATH_TMP = os.path.join(FOLDER, 'autoresume.tmp')
PAUSED = ADDON.getSetting('autoresume.paused')


def resume():
  # Wait for up to ten minutes for save folder to be available
  t_end = time.time() + 60 * 1
  while not os.path.exists(FOLDER) and time.time() < t_end:
    sleep(1)

  if not os.path.exists(FOLDER):
    logw("Failed to access autoresume.save.folder: %s" % FOLDER)
    return

  if not os.path.exists(PATH):
    logd("No autoresume file, nothing to resume: %s" % PATH)
    return

  # Read from autoresume.txt
  media_file = ''
  with open(PATH, 'r') as f:
    media_file = f.readline().rstrip('\n')
    position = float(f.readline())

  logi("Resuming %s at %f" % (media_file, position))

  # Play file and wait for up to 1m for playing to start
  logd("Play %s" % media_file)
  xbmc.Player().play(media_file)
  t_end = time.time() + 60
  while time.time() < t_end and not xbmc.Player().isPlaying():
    sleep(0.5)
  sleep(1)

  # If pause flag set pause the playback
  if PAUSED and xbmc.Player().isPlaying():
    logd("Pause %s" % media_file)
    xbmc.Player().pause()

  # Attempt to seek to last recorded position for up to 30s
  t_end = time.time() + 30
  while time.time() < t_end:
    logi("Seek %s to %f" % (media_file, position))
    xbmc.Player().seekTime(position)
    sleep(3)
    # Make sure it actually got there.
    if abs(position - xbmc.Player().getTime()) < 30:
      break


def record_position(prev_state):
  (prev_media_file, prev_position, prev_playing, count) = prev_state
  if xbmc.Player().isPlaying():
    media_file = xbmc.Player().getPlayingFile()
    position = xbmc.Player().getTime()
    logd("Currently playing %s at %f" % (media_file, position))
    # Write info to temp file, then actual file, try to make this idempotent
    if not xbmc.abortRequested and (not prev_playing or media_file != prev_media_file or position != prev_position):
      logd("Writing %s" % PATH_TMP)
      with open(PATH_TMP, 'w', 0) as f:
        f.write("%s\n%f" % (media_file, position))
      logd("Renaming %s to %s" % (PATH_TMP, PATH))
      os.rename(PATH_TMP, PATH)
    return (media_file, position, True, count + 1 if prev_playing else 1)
  else:
    logd("Nothing currently playing")
    if not prev_playing and count > 2 and os.path.exists(PATH) and not xbmc.abortRequested:
      logi("Nothing playing after %d checks, deleting %s" % (count, PATH))
      os.remove(PATH)
    return (None, None, False, count + 1 if not prev_playing else 1)


def logd(msg):
  xbmc.log("%s: %s" % (ADDON_ID, msg), xbmc.LOGDEBUG)


def logi(msg):
  xbmc.log("%s: %s" % (ADDON_ID, msg), xbmc.LOGINFO)


def logw(msg):
  xbmc.log("%s: %s" % (ADDON_ID, msg), xbmc.LOGWARNING)


if __name__ == "__main__":
  resume()
  state = (None, None, False, 0)
  t_last = time.time()
  while (not xbmc.abortRequested):
    if time.time() - t_last > FREQUENCY:
      state = record_position(state)
      t_last = time.time()
    sleep(1)
