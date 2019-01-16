
import configparser
import subprocess
import os


config = configparser.ConfigParser()
config.read('config.ini')
mkvtoolnix_path = config["DEPENDANCIES"]['mkvtoolnix_path']


def extract():
    """Get an answer."""
    subprocess.run([mkvtoolnix_path + os.sep + "mkvextract.exe"], shell=True, check=True)
    return True


extract()

