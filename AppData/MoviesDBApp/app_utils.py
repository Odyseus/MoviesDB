# -*- coding: utf-8 -*-
"""Summary

Attributes
----------
EXT : tuple
    A list of video files extensions.
movie_not_found : list
    Description
movies : list
    Description
not_a_movie : list
    Description
OMDB_URL : str
    Description
root_folder : str
    The main folder containing the Knowledge Base. All commands must be executed
    from this location without exceptions.
"""

import json
import os

from .python_utils import exceptions
from .python_utils import titlecase
from .python_utils import tqdm

try:
    import requests
except (SystemError, ImportError):
    raise exceptions.MissingDependencyModule("Module not installed: <requests>")

try:
    from guessit import guessit
except (SystemError, ImportError):
    raise exceptions.MissingDependencyModule("Module not installed: <guessit>2>")


root_folder = os.path.realpath(os.path.abspath(os.path.join(
    os.path.normpath(os.getcwd()))))


OMDB_URL = 'http://www.omdbapi.com/?'

EXT = (".3g2", ".3gp", ".3gp2", ".3gpp", ".60d", ".ajp", ".asf", ".asx", ".avchd", ".avi", ".bik",
       ".bix", ".box", ".cam", ".dat", ".divx", ".dmf", ".dv", ".dvr-ms", ".evo", ".flc", ".fli",
       ".flic", ".flv", ".flx", ".gvi", ".gvp", ".h264", ".m1v", ".m2p", ".m2ts", ".m2v", ".m4e",
       ".m4v", ".mjp", ".mjpeg", ".mjpg", ".mkv", ".moov", ".mov", ".movhd", ".movie", ".movx",
       ".mp4", ".mpe", ".mpeg", ".mpg", ".mpv", ".mpv2", ".mxf", ".nsv", ".nut", ".ogg", ".ogm",
       ".omf", ".ps", ".qt", ".ram", ".rm", ".rmvb", ".swf", ".ts", ".vfw", ".vid", ".video", ".viv",
       ".vivo", ".vob", ".vro", ".wm", ".wmv", ".wmx", ".wrap", ".wvx", ".wx", ".x264", ".xvid")


movies = []
not_a_movie = []
movie_not_found = []


def scan_directories(movies_paths, debug, logger):
    """Scan directories.

    Parameters
    ----------
    movies_paths : TYPE
        Description
    debug : TYPE
        Description
    logger : TYPE
        Description
    """
    data_from_files = {}
    errors = []

    # The following progress bars are kind of pointless.
    # All the directories are scanned in a fraction of a second.
    for mp in tqdm(movies_paths):
        for root, dirs, files in tqdm(os.walk(mp)):
            for filename in files:
                p = os.path.abspath(os.path.join(root, filename))

                if os.path.getsize(p) > (25 * 1024 * 1024):
                    try:
                        f_name, f_ext = os.path.splitext(filename)

                        if f_ext in EXT:
                            data_from_files[f_name] = p
                    except Exception as err:
                        errors.append(err)
                        continue  # This is kind of pointless.

    if errors:
        logger.error("Errors found while scaning directories.")
        logger.error("\n".join(errors), term=False, date=True)

    json_file = os.path.join(root_folder, "UserData", "1_data_from_files.json")

    with open(json_file, "w") as out:
        if debug:
            json.dump(data_from_files, out, indent=4)
        else:
            json.dump(data_from_files, out)


def generate_movies_base_data_from_file_names(debug, logger):
    """Summary

    Parameters
    ----------
    debug : TYPE
        Description
    logger : TYPE
        Description

    Raises
    ------
    RuntimeError
        Description
    """
    data_from_files = os.path.join(root_folder, "UserData", "1_data_from_files.json")
    movies_base_info = []
    movies_without_info = []
    json_data_from_file = None
    errors = []

    with open(data_from_files, "r") as file:
        json_data_from_file = json.loads(file.read())

    if json_data_from_file is None:
        raise RuntimeError("json_data_from_file is None")

    for movie_file_name in tqdm(json_data_from_file):
        movie_info_raw = dict(guessit(movie_file_name, options={
            "verbose": False,
            "type": "movie",
            "json": True,
            "name_only": True,
        }))

        movie_title = movie_info_raw.get("title", 0)
        # The dictionary returned by guessit contains keys impossible to directly encode to JSON.
        # Create a custom dict with only the data that I want/need and move on.
        movie_base_info = {
            "path_to_movie": json_data_from_file[movie_file_name],
            "file_name": movie_file_name,
            "title": titlecase(movie_title) if movie_title else movie_title,
            "year": movie_info_raw.get("year", 0),
            "cd": movie_info_raw.get("cd", 0),
            "format": movie_info_raw.get("format", 0),
            "screen_size": movie_info_raw.get("screen_size", 0),
            "video_codec": movie_info_raw.get("video_codec", 0),
            "release_group": movie_info_raw.get("release_group", 0),
            "type": movie_info_raw.get("type", 0),
        }

        try:
            if movie_base_info.get("title"):
                movies_base_info.append(movie_base_info)
            else:
                movies_without_info.append(movie_base_info)
        except Exception as err:
            errors.append(err)

    if errors:
        logger.error("Errors found while generating data from file names.")
        logger.error("\n".join(errors), term=False, date=True)

    movie_names = os.path.join(root_folder, "UserData", "2_movies_names.json")

    with open(movie_names, "w") as out:
        if debug:
            json.dump(movies_base_info, out, indent=4)
        else:
            json.dump(movies_base_info, out)


def get_movie_info(name):
    """Find movie information

    Parameters
    ----------
    name : TYPE
        Description

    Returns
    -------
    TYPE
        Description
    """
    movie_info = guessit(name)
    if movie_info['type'] == "movie":
        if 'year' in movie_info:
            return omdb(movie_info['title'], movie_info['year'])
        else:
            return omdb(movie_info['title'], None)
    else:
        not_a_movie.append(name)


def omdb(title, year):
    """Fetch data from OMDB API.

    Parameters
    ----------
    title : TYPE
        Description
    year : TYPE
        Description

    Returns
    -------
    TYPE
        Description
    """
    params = {'t': title.encode('ascii', 'ignore'),
              'plot': 'full',
              'type': 'movie',
              'tomatoes': 'true'}

    if year:
        params['y'] = year

    url = OMDB_URL + urlencode(params)
    return json.loads(requests.get(url).text)


if __name__ == "__main__":
    pass
