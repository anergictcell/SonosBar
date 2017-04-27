#!/usr/bin/env python -W ignore
# -*- coding: utf-8 -*-
"""
Control you Sonos system from you Mac Menu Bar
SonosBar is written to work with BitBar (https://github.com/matryer/bitbar)
and uses SoCo (https://github.com/SoCo/SoCo) as Sonos API
It can be used without BitBar as a command line interface for Sonos as well.

Do not use the files in the /src directory with BitBar directly,
instead use the sonosbar.py script that contains all source files
"""

import os
import sys

try:
    import soco
    from soco.music_services import MusicService
    from soco.data_structures import DidlItem, to_didl_string
except ImportError:
    print("Error")
    print("---")
    print("You need to istall >>soco<< | href=https://github.com/SoCo/SoCo")
    sys.exit(0)

from cli_arguments import ARGUMENTS
import bitbar_output
from bitbar_output import output_for_bitbar


bitbar_output.PATH_TO_SCRIPT = os.path.realpath(__file__)
GROUP = ARGUMENTS.group


def get_player_by_name(name):
    """Returns a SoCo object for the given name (if it exists)"""
    for device in soco.discover():
        if device.player_name == name:
            return device

def define_player(ip_address, name):
    """Returning a SoCo object of the chosen player"""
    player = None
    if ip_address:
        player = soco.SoCo(ip_address)
    if name:
        player = get_player_by_name(name)

    if player and GROUP:
        # Change player to be the coordinator of the group
        player = player.group.coordinator

    return player

def find_random_player():
    """Searches the network for Sonos zones and picks one randomly"""
    zones = soco.discover()

    if zones:
        # picking a random player
        player = next(iter(zones))
        return player

    return None

def parse_zone_groups(player):
    """Creates a list of all Zones with attrbute
    whether they are a group or a single player"""
    all_zones = []
    for group in player.all_groups:
        if len(group.members) > 1:
            all_zones.append({"kind":"G", "master":group.coordinator})
        else:
            all_zones.append({"kind":"P", "master":group.coordinator})
    return all_zones



def verbose_output(string):
    """Printing the passed commands to stdout"""
    if ARGUMENTS.verbose:
        print("{0}: {1}".format(
            ("Group " if GROUP else "Player "), string))

def group_coordinate(function):
    """Wrapper function to ensure unjoining for single players"""
    def inner_function(*arguments):
        """Inner function"""
        if GROUP:
            function(*arguments)
        else:
            # First argument always has to be the player SoCo object
            arguments[0].unjoin()
            function(*arguments)
    return inner_function

def get_songs_from_playlist(player, playlist_name):
    """Returns a list of songs from the given playlist"""
    lists = player.get_sonos_playlists()
    for playlist in lists:
        if playlist.title == playlist_name:
            return player.music_library.browse(playlist)

@group_coordinate
def play_playlist(player, playlist_name):
    """Replaces the queue with the selected playlist"""
    verbose_output("Play playlist {0}".format(playlist_name))
    songs = get_songs_from_playlist(player, playlist_name)
    player.clear_queue()
    for song in songs:
        player.add_to_queue(song)
    player.play_from_queue(0)

@group_coordinate
def play_radio_station(player, uri):
    """Plays the selected radio station. The URI must be in the
    format as it is currently returned from soco:
        x-sonosapi-stream:s25111?sid=254&flags=32
    """
    verbose_output("Switching to radio station {0}".format(uri))
    service = MusicService('TuneIn')
    didl = DidlItem(
        title="DUMMY", parent_id="DUMMY", item_id="DUMMY", desc=service.desc)
    meta = to_didl_string(didl)
    player.avTransport.SetAVTransportURI(
        [('InstanceID', 0), ('CurrentURI', uri), ('CurrentURIMetaData', meta)])
    player.play()

@group_coordinate
def play(player):
    """Play the selected song"""
    verbose_output("Play")
    player.play()

@group_coordinate
def pause(player):
    """Pause the current playback"""
    verbose_output("Pause")
    player.pause()

@group_coordinate
def next_track(player):
    """Play the next track"""
    verbose_output("Next track")
    player.next()

@group_coordinate
def previous_track(player):
    """Play the previous track"""
    verbose_output("Previous track")
    player.previous()

@group_coordinate
def turn_on_shuffle(player):
    """Turn on shuffle"""
    verbose_output("Shuffle ON")
    player.play_mode = "SHUFFLE_NOREPEAT"

@group_coordinate
def turn_off_shuffle(player):
    """Turn off shuffle"""
    verbose_output("Shuffle OFF")
    player.play_mode = "NORMAL"

def set_volume(player, volume):
    """Sets the volume"""
    verbose_output("Setting the volume to {0}".format(volume))
    player.volume = volume

def join(source, target):
    """Joining another group"""
    if target is None:
        return invalid_command("Target to join is not known")
    if GROUP:
        for single_player in source.group.members:
            single_player.join(target.group.coordinator)
    else:
        source.join(target.group.coordinator)

def invalid_command(err):
    """Handles errors and prints error messages"""
    print("ERROR: {0}".format(err))
    return

def main(args):
    """Main function"""
    player = define_player(args.ip, args.player)

    if player is None or args.bitbar:
        player = player or find_random_player()
        print_bitbar_controls(player)
        return

    if GROUP:
        # Change player to the coordinator of the group
        player = player.group.coordinator

    if args.playlist:
        return play_playlist(player, args.playlist)

    if args.radio:
        return play_radio_station(player, args.radio)

    if args.vol is not None:
        return set_volume(player, args.vol)

    if args.join:
        verbose_output("Joining {0}".format(args.join))
        to_join = define_player(None, args.join)
        return join(player, to_join)

    if args.ipjoin:
        verbose_output("Joining {0}".format(args.ipjoin))
        to_join = define_player(args.ipjoin, None)
        return join(player, to_join)

    if args.unjoin:
        verbose_output("Unjoin")
        player.unjoin()
        return

    if args.action is None:
        return

    if args.action.lower() == "play":
        play(player)
        return

    if args.action.lower() == "pause":
        pause(player)
        return

    if args.action.lower() == "next":
        next_track(player)
        return

    if args.action.lower() == "previous":
        previous_track(player)
        return

    if args.action.lower() == "shuffle":
        turn_on_shuffle(player)
        return

    if args.action.lower() == "normal":
        turn_off_shuffle(player)
        return

def print_bitbar_controls(player):
    """Prints the lines used for Bitbar to stdout"""
    if player is None:
        print("🔇 Sonos")
        print("---")
        print("No Sonos Zone present")
    else:
        output_for_bitbar(parse_zone_groups(player))

if __name__ == "__main__":
    main(ARGUMENTS)
