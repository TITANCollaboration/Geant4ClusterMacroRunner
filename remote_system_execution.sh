#!/bin/bash
# $1 = username
# $2 = hostname
# $3 = ssh port
# $4 = remote tmp directory
# $5 = base name for root and macro files
# $6 = local tmp directory to store all the macros, root files, and logs

#  This is for executing the g4 macros on remote systems where ssh will need to be employed

# Make sure the tmp directory exists on the remote host
#ssh $1@$2 -p $3 mkdir -p $4

# Copy over the macro file to remote host into tmp dir
scp -q -P $3 $6/$5.mac $1@$2:$4

# Execute command, move this over to the config file..
#ssh $1@$2 -p $3 "cd $4 && /vagrant/build/ebit ./$5.mac"
# Execute a docker instance...
ssh $1@$2 -p $3 "docker run --rm -v \$HOME/$4:/mydata decayspec-geant4-working /mydata/$5.mac"


# copy root file back here
scp -q -P $3 $1@$2:$4/$5.root $6
