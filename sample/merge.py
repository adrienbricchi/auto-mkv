
import configparser
import subprocess
import os
import glob
import itertools


config = configparser.ConfigParser()
config.read('config.ini')
mkvtoolnix_path = config["DEPENDANCIES"]['mkvtoolnix_path']


def parse_mkvinfo_result(lines):
    """Get an answer."""
    lines = list(itertools.dropwhile(lambda line: line != "|+ Tracks", lines))[1:]
    tracks = [list(group) for key, group in itertools.groupby(lines, lambda line: line == "| + Track") if not key]
    result = []
    for track in tracks:
        language_info = [info for info in track if info.startswith("|  + Language: ")] + ["|  + Language: und"]
        language = language_info[0][15:]
        media_info = [info for info in track if info.startswith("|  + Track type: ")] + ["|  + Track type: und"]
        media = media_info[0][15:]
        result += [(media, language)]
    return True


def determine_audio_tracks(file_path):
    """Get an answer."""
    result = subprocess.run([mkvtoolnix_path + os.sep + "mkvinfo.exe", file_path],
                            shell=True,
                            check=False,
                            encoding='utf-8',
                            stdout=subprocess.PIPE)
    parse_mkvinfo_result(result.stdout.split('\n'))
    return True


def extract(file_path, tracks):
    """Get an answer."""
    subprocess.run([mkvtoolnix_path + os.sep + "mkvextract.exe"], shell=True, check=True)
    return True


def extract_all_in_path(folder_path):
    """Get an answer."""
    files = glob.glob(folder_path + os.sep + "*.mkv")
    for file in files:
        print("File : " + file)
        determine_audio_tracks(file)
    return True


