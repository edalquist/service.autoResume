service.autoResume
==================

Kodi (XBMC / LibreELEC) service add-on that remembers what was playing and where it left off when power is abruptly cut off and restores the media and position it was playing when power is restored.

The intent of autoResume is for Kodi running in a car.  If using a Raspberry Pi, it's recommended that the "Save Folder" setting point to a folder that is not on your SD card that the RPi boots from to minimize the risk of XBMC doing any writes to the SD card at the time power is cut off.  If using an external USB drive for media, set the "Save Folder" setting to save there.

Install by downloading this repository, placing it in `/storage/.kodi/addons/`, and restarting Kodi. You must configure the addon to set a Save Folder before it will work.
