# -*- coding: utf-8 -*-

"""Generates Menus for Bitbar display"""

PATH_TO_SCRIPT = None

def output_for_bitbar(zones):
    """Prints the topology display"""
    print("🔊Sonos")
    print("---")
    for zone in zones:
        print_zone(zone)

def print_zone(zone):
    """Prints basic info about the zone and calls functions to
    print more detailed info"""
    print("---")
    print("Zone:")
    print("{0}: {1}".format(zone["kind"], zone["master"].player_name))
    if zone["kind"] == "P":
        print_single_player(zone["master"])
    else:
        print_group(zone["master"])

def print_single_player(player):
    """Controls printing of control elements for a single-player zone"""
    print_music_controls(player, "--")
    print_player_controls(player, "--")
    print_top_level_controls(player, "")

def print_group(master):
    """Controls printing of control elements for a multi-player zone"""
    print_music_controls(master, "--")
    print_top_level_controls(master, "")
    for player in master.group.members:
        print("➤ {0}".format(player.player_name))
        print_player_controls(player, "--")
        print("--Volume")
        print_volume_controls(player, "--")

def create_command(player, *params):
    """Creates the Bitbar specific command"""
    string = "bash={0} param1=-i param2={1}"
    i = 3
    for param in params:
        string += " param{0}={1}".format(i, param)
        i += 1
    string += " terminal=false refresh=true"
    return string.format(PATH_TO_SCRIPT, player.ip_address)

def print_player_controls(player, indent):
    """Prints Player controls for Bitbar"""

    print("{0}Join".format(indent))
    for single_player in player.all_zones:
        if single_player != player:
            print("{0}--{1} | ".format(indent, single_player.player_name) +
                  create_command(player, "--ipjoin", single_player.ip_address)
                 )
    print("{0}Unjoin | ".format(indent) +
          create_command(player, "--unjoin")
         )

def print_music_controls(player, indent):
    """Prints Music controls for Bitbar"""
    print("{0}Playlists".format(indent))
    for playlist in player.get_sonos_playlists():
        print("{0}--{1} | ".format(indent, playlist.title) +
              create_command(player, "-gl", '"' + playlist.title + '"')
             )

    print("{0}Radios".format(indent))
    for station in player.get_favorite_radio_stations()["favorites"]:
        print("{0}--{1} | ".format(indent, station["title"]) +
              create_command(player, "-gr", '"' + station["uri"] + '"')
            )

def print_top_level_controls(player, indent):
    """Prints the controls that are displayed on the base level for each
    player / group"""
    playing = player.get_current_transport_info()["current_transport_state"]
    if playing == "PLAYING":
        print("{0}├ Pause | ".format(indent) +
              create_command(player, "pause", "-g"))
        print("{0}├ Next | ".format(indent) +
              create_command(player, "next", "-g"))
    else:
        print("{0}├ Play | ".format(indent) +
              create_command(player, "play", "-g"))

    print("{0}└ Volume | ".format(indent))
    print_volume_controls(player, indent)

def print_volume_controls(player, indent):
    """Prints controls to adjust the volume"""
    for vol in range(0, 11):
        if (vol-1) * 10 < player.volume and vol*10 >= player.volume:
            # print checkmark
            print(("{0}--{1}{2}").format(indent, u'\u2713'.encode("utf-8"), vol))
        else:
            print("{0}--{1} | ".format(indent, vol) +
                  create_command(player, "--vol", vol*10)
                 )
