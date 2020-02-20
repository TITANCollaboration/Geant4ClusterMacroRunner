#!/bin/bash
# $1 = username
# $2 = hostname
# $3 = ssh port
# $4 = remote tmp directory
# $5 = base name for root and macro files
# $6 = local tmp directory to store all the macros, root files, and logs
#  This file is for locally running the GEANT4 macro, should be a bit simpler?  Maybe we'll never use it..
#


# Copy over the macro file to remote host into tmp dir
cp $6/$5.mac $HOME/$4

# Execute command, move this over to the config file..
#ssh $1@$2 -p $3 "cd $4 && /vagrant/build/ebit ./$5.mac"
# Execute a docker instance...

docker run --rm -v $HOME/$4:/mydata decayspec-geant4-working /mydata/$5.mac


# copy root file back here
cp $HOME/$4/$5.root $6
