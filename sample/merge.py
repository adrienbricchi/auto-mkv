
import configparser
import subprocess
import os
import glob
import itertools
from send2trash import send2trash


config = configparser.ConfigParser()
config.read('config.ini')
mkvextract = config["DEPENDANCIES"]['mkvtextract_path']
mkvinfo = config["DEPENDANCIES"]['mkvinfo_path']
eac3to = config["DEPENDANCIES"]['eac3to_path']
neroaac = config["DEPENDANCIES"]['nero_aac_path']


def delete(path):
    if config["PARAMETERS"]['use_trash']:
        send2trash(path)
    else:
        os.remove(path)


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
        extension = tracks[i][0] if tracks[i][0] != "truehd" else "thd"
        if extension in ("ac3", "dts", "thd"):
            track_name = file_path[:-4] + "_track" + str(i + 1) + "_" + tracks[i][1] + "_DELAY 0ms." + extension
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


def get_bitrates(file_path):
    root_folder = os.path.dirname(os.path.normpath(file_path))
    bitrate_file_candidates = glob.glob(root_folder + os.sep + "*.bitrate")
    if len(bitrate_file_candidates) == 1:
        file_bitrate = os.path.basename(bitrate_file_candidates[0])
        return file_bitrate[:-8].split("-")
    else:
        return ["096", "112", "128", "160", "192", "224", "256"]


def reencode_audio(folder_path):
    """Get an answer."""
    files = glob.glob(folder_path + os.sep + "**" + os.sep + "*.ac3", recursive=True)
    files += glob.glob(folder_path + os.sep + "**" + os.sep + "*.dts", recursive=True)
    files += glob.glob(folder_path + os.sep + "**" + os.sep + "*.thd", recursive=True)
    files.sort()

    for file in files:
        print("Reencode : " + file)
        bitrates = get_bitrates(file)
        if len(glob.glob(file + "_*")) == 0:
            for bitrate in bitrates:
                try:
                    subprocess.run(
                        [eac3to, file, "stdout.wav", "|",
                         neroaac, "-br", str(bitrate) + "000", "-if", "-", "-of", file + "_" + bitrate + ".aac"],
                        shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )
                    print("           " + str(bitrate))
                except subprocess.CalledProcessError:
                    print("           " + str(bitrate) + " error")
                    if len(glob.glob(file + "_" + bitrate + ".aac")) == 1:
                        delete(file + "_" + bitrate + ".aac")
            if len(glob.glob(file + "_*.aac")) > 0:
                delete(file)
    return True

