#!/usr/bin/python3
# -*-coding:utf8 -*

# auto-mkv
# Copyright (C) 2019-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import configparser
import subprocess
import os
import re
import glob
import itertools
from send2trash import send2trash

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

mkvextract = config["DEPENDANCIES"]['mkvtextract_path']
mkvmerge = config["DEPENDANCIES"]['mkvmerge_path']
mkvinfo = config["DEPENDANCIES"]['mkvinfo_path']
eac3to = config["DEPENDANCIES"]['eac3to_path']
neroaac = config["DEPENDANCIES"]['nero_aac_path']


def delete(path):
    if os.path.exists(path):
        if config["PARAMETERS"]['use_trash'] == "true":
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
        if extension in ("ac3", "dts", "eac3", "thd"):
            track_name = file_path[:-4] + "_track" + str(i + 1) + "_[" + tracks[i][1] + "]_DELAY 0ms." + extension
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
    files += glob.glob(folder_path + os.sep + "**" + os.sep + "*.eac3", recursive=True)
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
                    delete(file + "_" + bitrate + ".aac")
            if len(glob.glob(file + "_*.aac")) > 0:
                delete(file)
    return True


def remux_audio(folder_path):
    """Get an answer."""
    files = glob.glob(folder_path + os.sep + "**" + os.sep + "*.aac", recursive=True)
    files.sort()

    for file in files:
        print("Remux : " + file)
        file_remuxed = file[:-3] + "mka"
        try:
            subprocess.run(
                [mkvmerge, "--ui-language", "fr", "--sync", "0:0",
                 "--output", file_remuxed, "(", file, ")"],
                shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            delete(file)
        except subprocess.CalledProcessError:
            print("           " + " error")
            delete(file_remuxed)


def remux_file(path):
    """Get an answer."""
    print(path)

    todo_files = glob.glob(path + os.sep + "*.mux")
    if len(todo_files) == 0:
        return

    todo_file = todo_files[0]
    todo_string = os.path.basename(os.path.normpath(todo_file))[:-4]
    todo_string.split()
    print("todo : " + todo_string)
    fields = re.compile(r"\[(.*?)=(.*?)([+-]\d+)?\]+").findall(todo_string)

    files = glob.glob(path + os.sep + "*")
    files_groups = []
    buffer = []
    for file in files:
        if file.endswith(".mkv"):
            if len(buffer) > 0:
                files_groups.append(buffer.copy())
                buffer.clear()
        buffer.append(file)
    files_groups.append(buffer.copy())
    buffer.clear()

    for files_group in files_groups:
        print([i for i in files_group if i.endswith(".mkv")])
        command_line = [mkvmerge, "--ui-language", "fr"]
        complete = True

        for field in fields:
            current = []

            if field[0] == "video":
                current = [i for i in files_group if i.endswith(".mkv")]
            elif field[0] == "audio":
                current = [i for i in files_group
                           if (i.endswith(".aac") or i.endswith(".mka"))
                           and "[" + field[1] + "]" in i
                           ]
            elif field[0] == "sub":
                current = [i for i in files_group if i.endswith(".srt") and "[" + field[1] + "]" in i]
            elif field[0] == "cover":
                current = glob.glob(path + os.sep + field[1])

            if field[0] != "tag":

                if len(current) < 1:
                    print("    ... missing " + str(field))
                    complete = False
                    break
                elif len(current) > 1:
                    print("    ... undetermined" + str(field))
                    complete = False
                    break

                current_delay_string = re.compile(r"DELAY (.*?)ms").findall(current[0])
                current_delay = 0 if current_delay_string == [] else int(current_delay_string[0])
                set_delay_string = "+0" if not field[2] else field[2]
                set_delay = int(set_delay_string.replace("+", ""))
                final_delay = current_delay + set_delay

            if field[0] == "video":

                if config["PARAMETERS"]['use_dots_in_file_name'] == "true":
                    file_path = os.path.normpath(current[0])[:-4]
                    file_path = os.path.dirname(file_path) \
                        + os.sep \
                        + os.path.basename(file_path).replace(" ", ".") \
                        + ".().mkv"
                else:
                    file_path = os.path.normpath(current[0])[:-4] + " ().mkv"

                command_line.append("--output")
                command_line.append(file_path)
                command_line.append("--no-audio")
                command_line.append("--no-subtitles")
                command_line.append("--no-attachments")
                command_line.append("--language")
                command_line.append("0:" + field[1])
                command_line.append("--default-track")
                command_line.append("0:yes")
                command_line.append("(")
                command_line.append(os.path.normpath(current[0]))
                command_line.append(")")
            elif field[0] == "audio":
                command_line.append("--language")
                command_line.append("0:" + field[1])
                command_line.append("--sync")
                command_line.append("0:" + str(final_delay))
                command_line.append("(")
                command_line.append(os.path.normpath(current[0]))
                command_line.append(")")
            elif field[0] == "sub":
                command_line.append("--language")
                command_line.append("0:" + field[1])
                command_line.append("(")
                command_line.append(os.path.normpath(current[0]))
                command_line.append(")")
            elif field[0] == "cover":
                command_line.append("--attachment-name")
                command_line.append(os.path.basename(os.path.normpath(current[0])))
                command_line.append("--attachment-mime-type")
                command_line.append("image/jpeg")
                command_line.append("--attach-file")
                command_line.append(os.path.normpath(current[0]))
            elif field[0] == "tag":
                command_line.append("--title")
                command_line.append(field[1])

        if complete:
            command_line.append("--track-order")
            command_line.append(":0,".join([str(i) for i in range(0, len(fields) - 1)]) + ":0")
            print("complete : " + " ".join(command_line))
            try:
                subprocess.check_output(command_line)
            except subprocess.CalledProcessError as e:
                print(e.output)


test_path = config["PARAMETERS"]['test_path']
extract_all_in_path(test_path)
reencode_audio(test_path)
remux_audio(test_path)
remux_file(test_path)
