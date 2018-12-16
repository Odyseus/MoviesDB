#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Main command line application.

Attributes
----------
docopt_doc : str
    Used to store/define the docstring that will be passed to docopt as the "doc" argument.
root_folder : str
    The main folder containing the application. All commands must be executed from this location
    without exceptions.
"""

import os
import sys

from . import app_utils
from .__init__ import __appdescription__
from .__init__ import __appname__
from .__init__ import __status__
from .__init__ import __version__
from .python_utils import cli_utils

root_folder = os.path.realpath(os.path.abspath(os.path.join(
    os.path.normpath(os.getcwd()))))

docopt_doc = """{appname} {version} ({status})

{appdescription}

Usage:
    app.py (-h | --help | --manual | --version)
    app.py movies (scan | base_data | detailed_data) [--debug]
    app.py server (start | stop | restart)
                  [--host=<host>]
                  [--port=<port>]
    app.py generate system_executable

Options:

-h, --help
    Show this screen.

--manual
    Show this application manual page.

--version
    Show application version.

--host=<host>
    Host name. [Default: 0.0.0.0]

--port=<port>
    Port number. [Default: 8889]

--debug
    Debug.

Sub-commands for the `movies` command:
    scan                                Scan directories for movies.
    base_data                           Generate base movies data.
    detailed_data                       Generate detailed movies data.

Sub-commands for the `server` command:
    start                               Start server.
    stop                                Stop server.
    restart                             Restart server.

Sub-commands for the `generate` command:
    system_executable    Create an executable for this application on the system
                         PATH to be able to run it from anywhere.

""".format(appname=__appname__,
           appdescription=__appdescription__,
           version=__version__,
           status=__status__)


class CommandLineInterface(cli_utils.CommandLineInterfaceSuper):
    """Command line interface.

    It handles the arguments parsed by the docopt module.

    Attributes
    ----------
    a : dict
        Where docopt_args is stored.
    action : method
        Set the method that will be executed when calling CommandLineTool.run().
    """
    action = None

    def __init__(self, docopt_args):
        """
        Parameters
        ----------
        docopt_args : dict
            The dictionary of arguments as returned by docopt parser.
        """
        self.a = docopt_args
        self._cli_header_blacklist = [self.a["--manual"]]

        super().__init__(__appname__)

        if self.a["--manual"]:
            self.action = self.display_manual_page
        elif self.a["server"]:
            self.logger.info("**Command:** server")
            self.logger.info("**Arguments:**")

            if self.a["start"]:
                self.logger.info("start")
                self.action = self.http_server_start
            elif self.a["stop"]:
                self.logger.info("stop")
                self.action = self.http_server_stop
            elif self.a["restart"]:
                self.logger.info("restart")
                self.action = self.http_server_restart
        elif self.a["movies"]:
            if self.a["scan"]:
                self.logger.info("**Scanning directories...**")
                self.action = self.scan_directories
            elif self.a["base_data"]:
                self.logger.info("**Guessing movie names...**")
                self.action = self.generate_movies_base_data_from_file_names
            elif self.a["detailed_data"]:
                pass
        elif self.a["generate"]:
            if self.a["system_executable"]:
                self.logger.info("**System executable generation...**")
                self.action = self.system_executable_generation

    def run(self):
        """Execute the assigned action stored in self.action if any.
        """
        if self.action is not None:
            self.action()
            sys.exit(0)

    def scan_directories(self):
        """Summary
        """
        from runpy import run_path

        paths = run_path(os.path.join(root_folder, "UserData", "config.py"))["data"]["movies_paths"]
        app_utils.scan_directories(paths, self.a["--debug"], self.logger)

    def generate_movies_base_data_from_file_names(self):
        """Summary
        """
        app_utils.generate_movies_base_data_from_file_names(self.a["--debug"], self.logger)

    def system_executable_generation(self):
        """See :any:`cli_utils.CommandLineInterfaceSuper._system_executable_generation`.
        """
        self._system_executable_generation(
            exec_name="movies-db-cli",
            app_root_folder=root_folder,
            sys_exec_template_path=os.path.join(
                root_folder, "AppData", "data", "templates", "system_executable"),
            bash_completions_template_path=os.path.join(
                root_folder, "AppData", "data", "templates", "bash_completions.bash"),
            logger=self.logger
        )

    def http_server(self, action="start"):
        """Start/Stop/Restart the HTTP server.

        Parameters
        ----------
        action : str, optional
            Any of the following: start/stop/restart.
        """
        www_root = os.path.join(root_folder, "UserData", "www")
        os.chdir(www_root)
        cmd_path = os.path.join(root_folder, "AppData", "data", "python_scripts", "http_server")

        # Use of os.execv() so at the end only one process is left executing.
        # The "http_server" executable also uses os.execv() to launch the real web application.
        os.execv(cmd_path, [" "] + [action,
                                    "MoviesDB",
                                    self.a["--host"],
                                    self.a["--port"]])

    def http_server_start(self):
        """Self explanatory.
        """
        self.http_server(action="start")

    def http_server_stop(self):
        """Self explanatory.
        """
        self.http_server(action="stop")

    def http_server_restart(self):
        """Self explanatory.
        """
        self.http_server(action="restart")

    def display_manual_page(self):
        """See :any:`cli_utils.CommandLineInterfaceSuper._display_manual_page`.
        """
        self._display_manual_page(os.path.join(root_folder, "AppData", "data", "man", "app.py.1"))


def main():
    """Initialize command line interface.
    """
    cli_utils.run_cli(flag_file=".movies-db.flag",
                      docopt_doc=docopt_doc,
                      app_name=__appname__,
                      app_version=__version__,
                      app_status=__status__,
                      cli_class=CommandLineInterface)


if __name__ == "__main__":
    pass
