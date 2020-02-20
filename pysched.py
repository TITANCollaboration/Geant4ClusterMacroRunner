#!/usr/bin/env python
# Jon Ringuette - Feb 11th 2020

# This program should take the output of the EBITSIM's Geant4 macro output format and be able to
# break it up into individual tasks that can run independently.  It should then read in a config
# file of available systems, cores, etc.. and organize and run the GEANT4 macros on these cores
# it should also grab the root files when the runs are done and add them all together.
# It should also keep track of which processes have run and which have not to re-run any failed
# processes.  It should also use SSH as it's primary way to interact with remote systems to run
# tasks so we don't need a daemon.

import argparse
import configparser
import g4Macro
import sys
import os
from runSystems import Systems
from runSystems import process_event_loop


def initMacroMachine(system_objects, work_dir, g4_macro_filename):
    # This kicks off the entire process after any config file or command line argument stuff has happened
    for system in system_objects:
        print("Available System: %s" % system.hostname)
    g4_macro_object_list = g4Macro.read_in_geant4_macro_file(g4_macro_filename, work_dir)  # Change this to read from command line..
    process_event_loop(system_objects, g4_macro_object_list, work_dir)
    return 0


def processCommandLine(args):
    #  Process command line arguments and then call runSimulation()
    #  runSimulation(species, ebitParams, probeFnAddPop, outputConfig)
    initMacroMachine()
    return 0


def getConfigEntry(config, heading, item, reqd=False, remove_spaces=True, default_val=''):
    #  Just a helper function to process config file lines, strip out white spaces and check if requred etc.
    if config.has_option(heading, item):
        if remove_spaces:
            config_item = config.get(heading, item).replace(" ", "")
        else:
            config_item = config.get(heading, item)
    elif reqd:
        print("The required config file setting \'%s\' under [%s] is missing") % (item, heading)
        sys.exit(1)
    else:
        config_item = default_val
    return config_item


def processConfigFile(configFileName):
    config = configparser.RawConfigParser()

    if os.path.exists(configFileName):
        config.read(configFileName)

        systems_parameter_list = tuple(getConfigEntry(config, 'Run', 'systemsList', reqd=True, remove_spaces=True).split(","))
        work_dir = getConfigEntry(config, 'Run', 'work_dir', reqd=True, remove_spaces=True)
        g4_macro_filename = getConfigEntry(config, 'Run', 'g4_macro_filename', reqd=True, remove_spaces=True)

        system_objects = []
        for my_system in systems_parameter_list:
            # Read in Beam information
            hostname = getConfigEntry(config, my_system, 'hostname', reqd=True, remove_spaces=True)
            username = getConfigEntry(config, my_system, 'username', reqd=True, remove_spaces=True)
            ssh_port = int(getConfigEntry(config, my_system, 'ssh_port', reqd=True, remove_spaces=True))
            is_local = getConfigEntry(config, my_system, 'is_local', reqd=True, remove_spaces=True)
            thread_count = int(getConfigEntry(config, my_system, 'thread_count', reqd=True, remove_spaces=True))
            tmp_dir = getConfigEntry(config, my_system, 'tmp_dir', reqd=True, remove_spaces=True)

            system_objects.append(Systems(hostname, username, is_local, thread_count, tmp_dir, ssh_port))

        initMacroMachine(system_objects, work_dir, g4_macro_filename)


def main():

    parser = argparse.ArgumentParser(description='Geant4 Macro Scheduler')

    parser.add_argument('--configFile', dest='configFile', required=False,
                        help="Specify the complete path to the config file, by default we'll use g4macsched.cfg")

    parser.set_defaults(configFile="g4macsched.cfg")

    args, unknown = parser.parse_known_args()
    processConfigFile(args.configFile)


if __name__ == "__main__":
    main()
