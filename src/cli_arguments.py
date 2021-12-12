"""
Parses command line arguments for SonosBar

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
"""

import argparse
import socket

def parse_ip(ip_string):
    """Parsing the user supplied IP address to use on the local subnet"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('1.1.1.1', 1))  # we can use any IP here
    host_ip = s.getsockname()[0]
    subnets = host_ip.split(".")
    sonos_subnets = ip_string.split(".")
    new_ip = subnets[0:(4-len(sonos_subnets))] + sonos_subnets
    return ".".join(new_ip)


def parse_cli_arguments():
    """Main function that parses command line arguments"""
    parser = argparse.ArgumentParser(description='Control your Sonos')

    player_args = parser.add_mutually_exclusive_group()
    player_args.add_argument(
        "-p", "--player",
        metavar="SPEAKER_NAME",
        type=str,
        # default="Living Room",
        help="The name of the player/zone")

    player_args.add_argument(
        "-i", "--ip",
        metavar="IP_ADDRESS",
        type=str,
        help="The IP address of the player/zone")

    control_args = parser.add_mutually_exclusive_group()
    control_args.add_argument(
        "-l", "--playlist",
        metavar="PLAYLIST_NAME",
        type=str,
        help="The name of the playlist to play")

    control_args.add_argument(
        "-r", "--radio",
        metavar="RADIO_STATION",
        type=str,
        help="The name of the radio station to play")

    control_args.add_argument(
        "-v", "--vol",
        metavar="VOLUME",
        type=int,
        choices=range(0, 101),
        help="0-100")

    control_args.add_argument(
        "-j", "--join",
        metavar="SPEAKER_NAME",
        type=str,
        help="Name of the speaker to join")

    control_args.add_argument(
        "-k", "--ipjoin",
        metavar="SPEAKER_IP",
        type=str,
        help="IP of the speaker to join")

    control_args.add_argument(
        "-u", "--unjoin",
        action='store_const',
        const=True,
        help="Unjoin the player from all groups")

    control_args.add_argument(
        'action',
        metavar='action',
        nargs="?",
        choices=["play", "pause", "next", "previous", "shuffle", "normal"],
        help="""Action to take if non is set via flags.
          Can be either: play, pause, next, previous, shuffle, normal""")

    parser.add_argument(
        "-g", "--group",
        action='store_const',
        const=True,
        help="Apply the action to the whole group")

    output = parser.add_mutually_exclusive_group()
    output.add_argument(
        "-o", "--verbose",
        action='store_const',
        const=True,
        help="Display feedback about current actions")

    output.add_argument(
        "-b", "--bitbar",
        action='store_const',
        const=True,
        help="Display bitbar controls")

    args = parser.parse_args()

    if args.ip:
        args.ip = parse_ip(args.ip)

    if args.ipjoin:
        args.ipjoin = parse_ip(args.ipjoin)

    return args

ARGUMENTS = parse_cli_arguments()
