#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Summary

Attributes
----------
bottle_app : object
    Bottle application.
dir_path : str
    Extra path to look for modules to import.
root_folder : str
    The path to the folder that will be served by the web server.
"""
import os
import sys

from subprocess import call

try:
    from python_utils import bottle
except (ImportError, SystemError):
    from .python_utils import bottle

root_folder = os.path.realpath(os.path.abspath(os.path.join(
    os.path.normpath(os.getcwd()))))

bottle_app = bottle.Bottle()


class MoviesDBWebapp():
    """Movies Data Base web server.

    Attributes
    ----------
    host : str
        The host name used by the web server.
    port : str
        The port number used by the web server.
    """

    def __init__(self, host, port):
        """Initialization.

        Parameters
        ----------
        host : str
            The host name used by the web server.
        port : str
            The port number used by the web server.
        """
        self.host = host
        self.port = port

    def run(self):
        """Run web application.
        """
        bottle_app.run(host=self.host, port=self.port)

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
        return bottle.static_file(filepath, root=os.path.join(root_folder, "assets"))

    @bottle_app.route("/")
    def index():
        """Serve the landing page.

        Returns
        -------
        sre
            The content for the landing page.
        """
        with open(os.path.join(root_folder, "index.html"), "r") as file:
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
if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) == 2:
        app = MoviesDBWebapp(args[0], args[1])
        app.run()
