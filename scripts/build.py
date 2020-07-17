#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

'''
Script to "Build" my test project Jurassic.
'''

# Standard Python Imports
# -----------------------------------------------------------------------------
from datetime import datetime
import multiprocessing
import sys
import os
import subprocess
import argparse
import shutil

# Local/Internal Python Imports
#------------------------------------------------------------------------------
import jurassic


# Global Variables
#------------------------------------------------------------------------------
ALL_TARGETS = [prod + '-' + sec for prod in jurassic.products for sec in jurassic.securities]
DEFAULT_BUILD_DIR = 'build'
SUCCESS = 0
FAIL = 1


def run_command(command, logFile=None):

    sinks = []
    if logFile is not None:
        sinks.append(open(logFile, "a"))
    sinks.append(sys.stdout)

    print("Running '{}'".format(" ".join(command)))
    sys.stdout.flush()

    cmake = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while cmake.poll() is None:
        input = cmake.stdout.readline(16)
        if input:
            for sink in sinks:
                sink.write(input)

    while True:
        input = cmake.stdout.read(1)
        if input:
            for sink in sinks:
                sink.write(input)
        else:
            break

    return cmake.returncode


class Build(object):
    '''Execute a Jurassic build.'''

    def __init__(self, args):

        self.targets    = args.target_list
        self.num_jobs   = args.jobs
        self.build_dir  = args.build_dir
        self.work_dir   = os.getcwd()
        self.logFile    = "build.log"
        self.build_type = args.build_type

        if self.build_dir is None:
            self.build_dir = os.path.join(self.work_dir, DEFAULT_BUILD_DIR)

        # Clean and/or create build directory
        if os.path.exists(self.build_dir):
            if args.clean:
                print("Deleting " + self.build_dir)
                shutil.rmtree(self.build_dir)
        
        if not os.path.exists(self.build_dir):
            print("Creating " +  self.build_dir)
            os.makedirs(self.build_dir)

    def __print_details(self):
        '''Function to print details of this machine.'''
        print(run_command('cmake --version'))
        print(run_command('clang --version'))

    def init_log_file(self):
        '''Init the log file for the build'''
        if os.path.exists(self.logFile):
            os.remove(self.logFile)

    def run(self):
        '''Run the build with the specified flags.'''

        rc = SUCCESS

        # Only build if targets were specified
        if len(self.targets) == 0:
            return rc

        saved_wd = os.getcwd()
        os.chdir(self.build_dir)

        command = ['cmake', '--warn-uninitialized', '-Wdev', '-GNinja']

        if self.build_type is not None:
            command.append('-DTARGET_BUILD_TYPE=' + self.build_type)

        command.append(self.work_dir)

        rc = run_command(command, self.logFile)

        if rc != SUCCESS:
            print("FAILED")
            return rc

        print("Building '{}'".format(", ".join(self.targets)))

        # make command via Ninja
        # (Ninja version per platform is defined already in the /CMakeLists.txt)
        command = ['ninja', '-j{}'.format(str(self.num_jobs)), ' '.join(self.targets)]

        rc = run_command(command, self.logFile)
        if rc != 0:
            print("FAILED")
            return rc

        os.chdir(saved_wd)
        return rc


def process_command_line():
    '''Function to process command line arguments for this build.py script.'''

    target_list_choices = ALL_TARGETS + \
                         ['all-' + sec for sec in jurassic.securities] + \
                         [prod + '-all' for prod in jurassic.products] + \
                         ['all-all']

    parser = argparse.ArgumentParser(description='A script that build the Jurassic firmware.',
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("target_list",
                        nargs="*",
                        default="all-all",
                        choices=target_list_choices,
                        help="A space delimited list of targets to build.")
    
    parser.add_argument("-j", "--jobs",
                        type=int,
                        default=int(multiprocessing.cpu_count()),
                        help="Number of jobs to spawn.")

    parser.add_argument("-c", "--clean",
                        action="store_true",
                        default=False,
                        help="Deletes the contents of the build directory.")

    parser.add_argument("-t", "--build-type", "--code-type",
                        dest='build_type',
                        choices=jurassic.build_types,
                        default="LOCAL",
                        help="Build/code type of image files.")

    parser.add_argument("--build-dir", action="store",
                        dest="build_dir", default=None,
                        help="Specify the path to the desired build directory from the work directory.")

    args = parser.parse_args()

    # For some odd reason Argparse cannot handle a default value of a list for the target_list argument.
    # To work around this the default is the "all-all" string.
    # Convert the default value to a list for consistent processing later.
    if args.target_list == "all-all":
        args.target_list = ["all-all"]

    return args


def main():

    args = process_command_line()

    this_build = Build(args)

    start = datetime.now()

    rc = this_build.run()

    end = datetime.now()

    print("Completed in %s" % (end - start))

    if rc != 0:
        sys.exit(rc)


if __name__ == "__main__":
    main()