#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Web application.

Attributes
----------
www_root : str
    The path to the folder that will be served by the web server.
"""
import os
import sys

from subprocess import call

try:
    # If executed as a script to start the web server.
    host, port, app_dir_path = sys.argv[1:]
except Exception:
    # If imported as a module by Sphinx.
    host, port = None, None
    app_dir_path = os.path.realpath(os.path.abspath(os.path.join(
        os.path.normpath(os.path.dirname(__file__)))))

sys.path.insert(0, app_dir_path)

from python_utils.bottle_utils import WebApp
from python_utils.bottle_utils import bottle
from python_utils.bottle_utils import bottle_app

www_root = os.path.realpath(os.path.abspath(os.path.join(
    os.path.normpath(os.getcwd()))))


class MoviesDBWebapp(WebApp):
    """Web server.
    """

    def __init__(self, *args, **kwargs):
        """Initialization.

        Parameters
        ----------
        *args
            Arguments.
        **kwargs
            Keyword arguments.
        """
        super().__init__(*args, **kwargs)

    @bottle_app.route("/assets/<filepath:path>")
    def server_static(filepath):
        """Serve static files.

        Parameters
        ----------
        filepath : str
            Path to the served static file.

        Returns
        -------
        object
            An instance of bottle.HTTPResponse.
        """
        return bottle.static_file(filepath, root=os.path.join(www_root, "assets"))

    @bottle_app.route("/")
    def index():
        """Serve the landing page.

        Returns
        -------
        sre
            The content for the landing page.
        """
        with open(os.path.join(www_root, "index.html"), "r") as file:
            file_data = file.read()

        return file_data

    # Non-existent location. It's used just to "catch" POST requests.
    @bottle_app.post("/local_videos")
    def handle_video_path():
        """Handle video path.
        """
        video_path = os.path.abspath(bottle.request.POST["path"])
        video_folder = os.path.dirname(video_path)
        video_filename = os.path.basename(video_path)

        call(["xdg-open", video_filename], cwd=video_folder)


# FIXME: Convert this script into a module.
# Just because it's the right thing to do.
# As it is right now, everything works as "it should".
if __name__ == "__main__" and host and port:
    app = MoviesDBWebapp(host, port)
    app.run()
