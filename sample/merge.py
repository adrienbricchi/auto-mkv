
import configparser
import subprocess
import os
import glob
import itertools


config = configparser.ConfigParser()
config.read('config.ini')
mkvextract = config["DEPENDANCIES"]['mkvtextract_path']
mkvinfo = config["DEPENDANCIES"]['mkvinfo_path']
eac3to = config["DEPENDANCIES"]['eac3to_path']
neroaac = config["DEPENDANCIES"]['nero_aac_path']


def parse_mkvinfo_result(lines):
    """Get an answer."""
    lines = list(itertools.dropwhile(lambda line: line != "|+ Tracks", lines))[1:]
    tracks = [list(group) for key, group in itertools.groupby(lines, lambda line: line == "| + Track") if not key]
    result = []
    for track in tracks:
        language_info = [info for info in track if info.startswith("|  + Language: ")] + ["|  + Language: eng"]
        language = language_info[0][15:]
        codec_info = [info for info in track if info.startswith("|  + Codec ID: ")] + ["|  + Track type: eng"]
        codec = codec_info[0][17:].lower()
        result += [(codec, language)]
    return result


def retrieve_tracks(file_path):
    """Get an answer."""
    result = subprocess.run([mkvinfo, file_path], shell=True, check=False, encoding='utf-8', stdout=subprocess.PIPE)
    return parse_mkvinfo_result(result.stdout.split('\n'))


def extract_audio(file_path):
    """Get an answer."""
    tracks = retrieve_tracks(file_path)
    for i in range(0, len(tracks)):
        if tracks[i][0] == "ac3" or tracks[i][0] == "dts":
            track_name = file_path[:-4] + "_track" + str(i + 1) + "_" + tracks[i][1] + "_DELAY 0ms." + tracks[i][0]
            if not os.path.exists(track_name):
                subprocess.run([mkvextract, file_path, "tracks", str(i) + ":" + track_name], shell=True, check=True)
    return True


def extract_all_in_path(folder_path):
    """Get an answer."""
    files = glob.glob(folder_path + os.sep + "**" + os.sep + "*.mkv", recursive=True)
    for file in files:
        if len(glob.glob(file[:-4] + "_*")) == 0:
            extract_audio(file)
    return True


def reencode_audio(folder_path):
    """Get an answer."""
    files = glob.glob(folder_path + os.sep + "**" + os.sep + "*.ac3", recursive=True)
    files += glob.glob(folder_path + os.sep + "**" + os.sep + "*.dts", recursive=True)
    files.sort()
    for file in files:
        print("Reencode : " + file)
        if len(glob.glob(file + "_*")) == 0:
            for bitrate in ["096", "112", "128", "160", "192", "224", "256"]:
                try:
                    subprocess.run(
                        [eac3to, file, "stdout.wav", "|",
                         neroaac, "-br", bitrate + "000", "-if", "-", "-of", file + "_" + bitrate + ".aac"],
                        shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )
                    print("           " + bitrate)
                except subprocess.CalledProcessError:
                    print("           " + bitrate + " error")
                    if len(glob.glob(file + "_" + bitrate + ".aac")) == 1:
                        os.remove(file + "_" + bitrate + ".aac")
            if len(glob.glob(file + "_*.aac")) > 0:
                os.remove(file)
    return True

