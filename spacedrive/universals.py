#from direct.directnotify.DirectNotify import DirectNotify
#log = DirectNotify().newCategory("SpaceDrive")

from panda3d.core import LPoint3d, NodePath

# Physics constants
G = 6.67e-11

run_client = False
run_server = False

defaultSOIid = None #client
shipid = None #client

spawn = LPoint3d(0, 0, 0)

# Connivance constant, number of seconds in an Earth day
SECONDSINDAY = 86400

# Time acceleration factor
# Default is 31,536,000 (365.25*24*60), or the earth orbits the sun in one minute
#TIMEFACTOR = 525969.162726
# Factor where it orbits once every 5 minutes
#TIMEFACTOR = 105193.832545
# Once an hour
#TIMEFACTOR = 8766.1527121
# Once a day
#TIMEFACTOR = 365.256363004
# Realtime
#TIMEFACTOR = 1
TIMEFACTOR = 100.0

# Julian day based on J2000.
#day = 9131.25
day = 9031.25

# Keeps track of the user name of the client
username = "Moofoo"

#apollo specific
#playerStations = ['navigation', 'mainScreen', 'weapons']

#Conversion factor from SI to units used in engine
CONVERT = 1000.0

def get_day_in_seconds():
    return day * 86400