## SonosBar

### Control your Sonos system right from your Mac Menu Bar

![alt text](https://raw.githubusercontent.com/anergictcell/SonosBar/master/resources/SonosBar.png "Screenshot of SonosBar")

This is still a kind of experimental thing, working on it to learn Python programing.

You can also use it as a command line interface for Sonos:

##### Play the Sonos playlist Relax Music in the Living Room
```shell
./sonosBar.py -p "Living Room" -l "Relax Music"
```

##### Add the Master Bedroom player to the Living Room group
```shell
./sonosBar.py -p "Master Bedroom" -j "Living Room"
```

##### Pause the playback of the group
```shell
./sonosBar.py -gp "Master Bedroom" pause
```

### Command line API:
```
Define which Sonos player to use for controlling
-p --player    Name of the Sonos Player (eg: "Living Room")
-i --ip        IP address of the Sonos Player

=> IP addresses can be shortened if on the same subnet.
    eg: 192.168.1.15 can be chosen entering 15 when remote is also within
    192.168.1.x subnet

-l --playlist  Selects a playlist to play (from Sonos playlists)
-r --radio     Selects a radiostation to play
               eg: x-sonosapi-stream:s25111?sid=254&flags=32

-j --join       Join another player/group
                use the name of the player to be joined
-k --ipjoin     Join another payer/group
                use the IP address of the player to be joined

-v --vol        Change volume (1-100)

FLAGS
-g --group      Apply the chosen action to the whole group
                If not set, only the selected player performs the action
-u --unjoin     Unjoin from current group
-o --verbose    Display which action was just taken
-b --bitbar     Output system information for BitBar

ACTIONS
- play
- pause
- next
- previous
- shuffle
- normal (disable shuffle)
```