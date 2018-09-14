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

from runpy import run_path

from . import app_utils
from .__init__ import __appname__, __appdescription__, __version__, __status__
from .python_utils import exceptions, log_system, shell_utils, file_utils
from .python_utils.docopt import docopt

if sys.version_info < (3, 5):
    raise exceptions.WrongPythonVersion()

root_folder = os.path.realpath(os.path.abspath(os.path.join(
    os.path.normpath(os.getcwd()))))

# Store the "docopt" document in a variable to SHUT THE HELL UP Sphinx.
docopt_doc = """{__appname__} {__version__} {__status__}

{__appdescription__}

Usage:
    app.py movies (scan | base_data | detailed_data) [--debug]
    app.py server (start | stop | restart)
                  [--host=<host>]
                  [--port=<port>]
    app.py generate system_executable
    app.py (-h | --help | --version)

Options:

-h, --help
    Show this screen.

--version
    Show application version.

--host=<host>]
    Host name. [Default: 0.0.0.0]

--port=<port>]
    Port name. [Default: 8889]

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

""".format(__appname__=__appname__,
           __appdescription__=__appdescription__,
           __version__=__version__,
           __status__=__status__)


class CommandLineTool():
    """Command line tool.

    It handles the arguments parsed by the docopt module.

    Attributes
    ----------
    action : method
        Set the method that will be executed when calling CommandLineTool.run().
    debug : bool
        Perform extra debugging tasks.
    host : str
        Host name used by the web server.
    logger : object
        See <class :any:`LogSystem`>.
    port : int
        Port number used by the web server.
    """

    def __init__(self, args):
        """
        Parameters
        ----------
        args : dict
            The dictionary of arguments as returned by docopt parser.
        """
        super(CommandLineTool, self).__init__()
        self.debug = args["--debug"]
        self.action = None
        self.host = args["--host"]
        self.port = args["--port"]
        logs_storage_dir = "UserData/logs"
        log_file = log_system.get_log_file(storage_dir=logs_storage_dir,
                                           prefix="CLI")
        file_utils.remove_surplus_files(logs_storage_dir, "CLI*")
        self.logger = log_system.LogSystem(filename=log_file,
                                           verbose=True)

        self.logger.info(shell_utils.get_cli_header(__appname__), date=False)
        print("")

        if args["server"]:
            self.logger.info("Command: server")
            self.logger.info("Arguments:")

            if args["start"]:
                self.logger.info("start")
                self.action = self.http_server_start
            elif args["stop"]:
                self.logger.info("stop")
                self.action = self.http_server_stop
            elif args["restart"]:
                self.logger.info("restart")
                self.action = self.http_server_restart

        elif args["movies"]:
            if args["scan"]:
                self.logger.info("Scanning directories...")
                self.action = self.scan_directories
            elif args["base_data"]:
                self.logger.info("Guessing movie names...")
                self.action = self.generate_movies_base_data_from_file_names
            elif args["detailed_data"]:
                pass

        elif args["generate"]:
            if args["system_executable"]:
                self.logger.info("System executable generation...")
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
        paths = run_path(os.path.join(root_folder, "UserData", "config.py"))["data"]["movies_paths"]
        app_utils.scan_directories(paths, self.debug, self.logger)

    def generate_movies_base_data_from_file_names(self):
        """Summary
        """
        app_utils.generate_movies_base_data_from_file_names(self.debug, self.logger)

    def system_executable_generation(self):
        """See :any:`template_utils.system_executable_generation`
        """
        from .python_utils import template_utils

        template_utils.system_executable_generation(
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
        # The "http_server" executable could be inside app's AppData folder.
        # (The app was made standalone)
        cmd_path = os.path.join(root_folder, "AppData", "data", "python_scripts", "http_server")

        if not os.path.exists(cmd_path):
            # The app wasn't made standalone, so the "http_server" executable
            # is inside the main app (__app__).
            cmd_path = os.path.join(os.path.join(root_folder, ".."), "__app__",
                                    "data", "python_scripts", "http_server")

        # Use of os.execv() so at the end only one process is left executing.
        # The "http_server" executable also uses os.execv() to launch the real web application.
        os.execv(cmd_path, [" "] + [action,
                                    "MoviesDB",
                                    self.host,
                                    self.port])

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


def main():
    """Initialize main command line interface.

    Raises
    ------
    exceptions.BadExecutionLocation
        Do not allow to run any command if the "flag" file isn't
        found where it should be. See :any:`exceptions.BadExecutionLocation`.
    """
    if not os.path.exists(".movies-db.flag"):
        raise exceptions.BadExecutionLocation()

    arguments = docopt(docopt_doc, version="%s %s %s" % (__appname__, __version__, __status__))
    cli = CommandLineTool(arguments)
    cli.run()


if __name__ == "__main__":
    pass
