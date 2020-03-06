#!/bin/bash
cd /mydata
source /usr/local/geant4/geant4.10.05.p01/bin/geant4.sh
source /usr/local/root/root-6.14.06/bin/thisroot.sh
/tmp/build/ebit $@
