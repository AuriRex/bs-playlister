import os
import json
import xml.etree.ElementTree as ET
import hashlib
import datetime

beat_saber_path = "O:/SteamLibrarySSD/steamapps/common/Beat Saber/"

default_custom_levels_dir = "Beat Saber_Data/CustomLevels"

songcore_folder_data_path = "UserData/SongCore/folders.xml"

tempfolder = "./1988c (Paranoia - Kival Evan & xScaramouche)"


def create_playlist(title :str, author :str = "", description :str = "") -> dict:
    playlist = {}
    playlist["AllowDuplicates"] = False
    playlist["playlistTitle"] = title
    playlist["playlistAuthor"] = author
    playlist["playlistDescription"] = description
    playlist["songs"] = []
    return playlist

def is_custom_level_folder(folderpath :str) -> bool:
    return os.path.exists(folderpath + "/info.dat")



def add_hash_to_playlist(playlist :dict, level_hash :str) -> dict:
    if not level_hash in playlist["songs"]:
        playlist["songs"].append({"hash": level_hash})
    return playlist

def hash_folder(folderpath :str, printthing :bool = True) -> str:
    allbytes = bytearray(0)

    try:
        with open(folderpath + "/info.dat", "r") as file:
            string = file.read()

        with open(folderpath + "/info.dat", "rb") as file:
            allbytes = file.read()

        info_dot_dat = json.loads(string)


        for diffset in info_dot_dat["_difficultyBeatmapSets"]:
            #print(diffset["_beatmapCharacteristicName"])
            for difficulty in diffset["_difficultyBeatmaps"]:
                #print(difficulty["_difficulty"])
                filename = difficulty["_beatmapFilename"]
                #print(filename)
                with open(folderpath + "/" + filename, "rb") as file:
                    allbytes = allbytes + file.read()

        level_hash = hashlib.sha1(allbytes).digest().hex().upper()

        if printthing:
            print(info_dot_dat["_songName"] + " " + info_dot_dat["_songSubName"] + " - " + info_dot_dat["_songAuthorName"] + " | Mapped by: \"" + info_dot_dat["_levelAuthorName"] + "\", Hash:" + level_hash)
        
        return level_hash
    except Exception as ex:
        print("[ERROR] Level Hashing for folder \"" + folderpath + "\" failed: " + str(ex))
        return ""

def get_extra_song_folders(songcore_folder_dot_xml :str, include_wip :bool = False) -> list:
    extras = []

    file = ET.parse(songcore_folder_dot_xml)
    root = file.getroot()
    for folder in root:
        name = folder.find('Name').text
        path = folder.find('Path').text
        pack = int(folder.find('Pack').text)
        is_wip = folder.find('WIP').text == "True"
        image_path = folder.find('ImagePath').text
        print("Name:" + name + ", Path:" + path + ", IsWIP:" + str(is_wip) + ", Pack:" + str(pack) + ", ImagePath:" + image_path)

        if not include_wip and is_wip:
            print("Skipping \"" + name + "\" as it's a WIP pack!")
            continue

        extras.append({"name": name, "path": path, "pack": pack, "wip": is_wip, "imagepath": image_path})

    return extras

def set_paths(beatsaber_install_path :str):
    global beat_saber_path, default_custom_levels_dir, songcore_folder_data_path

    if beatsaber_install_path[-1:] == "/" or beatsaber_install_path[-1:] == "\\":
        beatsaber_install_path = beatsaber_install_path[:-1]

    beat_saber_path = beatsaber_install_path

    default_custom_levels_dir = beatsaber_install_path + "/Beat Saber_Data/CustomLevels"

    songcore_folder_data_path = beatsaber_install_path + "/UserData/SongCore/folders.xml"

    print(beat_saber_path)
    print(default_custom_levels_dir)
    print(songcore_folder_data_path)

def add_all_custom_songs_in_folder_to_playlist(playlist :dict, folderpath :str) -> dict:
    dirs = next(os.walk(folderpath))[1]
    for level_directory in dirs:
        absolute_level_path = folderpath + "/" + level_directory

        if is_custom_level_folder(absolute_level_path):
            level_hash = hash_folder(absolute_level_path)
            if not (level_hash == ""):
                add_hash_to_playlist(playlist, level_hash)
    
    return playlist

if __name__ == "__main__":
    # set_paths("O:/SteamLibrarySSD/steamapps/common/Beat Saber/")
    
    # playlist = create_playlist("All My Songs", "AuriRex", "Date Created: " +str(datetime.date.today()))

    # add_all_custom_songs_in_folder_to_playlist(playlist, default_custom_levels_dir)

    path_is_invalid = True
    bs_path = ""
    while path_is_invalid:
        bs_path = input("Provide BeatSaber Install Path> ")
        set_paths(bs_path)
        if os.path.exists(beat_saber_path + "/Beat Saber.exe"):
            path_is_invalid = False

    playlist = create_playlist("All My Songs", "AuriRex", "Date Created: " +str(datetime.date.today()))

    print("[INFO] Adding all songs from the defualt song folder at \"" + default_custom_levels_dir + "\"!")
    playlist = add_all_custom_songs_in_folder_to_playlist(playlist, default_custom_levels_dir)

    extras = None
    try:
        extras = get_extra_song_folders(songcore_folder_data_path)

        for extra in extras:
            print("[INFO] Adding all songs from the \"" + extra["name"] + "\" song folder at \"" + extra["path"] + "\"!")
            playlist = add_all_custom_songs_in_folder_to_playlist(playlist, extra["path"])
    except Exception as ex:
        print("[WARN] Something went wrong with extra song folders, if you don't have any set up ignore this!")
        print(ex)

    playlist_save_path = "./playlist.json"
    with open(playlist_save_path, "w") as file:
        file.write(json.dumps(playlist))
        print("Written playlist to file \"" + playlist_save_path + "\". It contains " + str(len(playlist["songs"])) + " songs!")

    # level_hash = hash_folder(tempfolder)
    # print(level_hash)
    # playlist = create_playlist("Title", "Meee", "cool playlist")
    # playlist = add_hash_to_playlist(playlist, level_hash)
    # print(json.dumps(playlist))
