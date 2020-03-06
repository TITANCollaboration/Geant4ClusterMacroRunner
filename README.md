# Geant4ClusterMacroRunner

![](https://github.com/TITANCollaboration/Geant4ClusterMacroRunner/blob/master/images/simulationstack.png)

This piece of software was initially intended to tie together the [EBIT Charge Breeding Simulator](https://github.com/TITANCollaboration/ebitsim) and [EBIT 8pi GEANT4 Simulator](https://github.com/TITANCollaboration/decayspec_8pi_geant4sim) software packages.  But it might be useful for more than that so lets go through a little bit of how it works and how I run it.

My goal was to write a small piece of flexible software that could accept a large number of GEANT4 macros and run them on various systems that I have access to and then have the output data (in this case ROOT files) available to me in a single location.  The GEANT4 simulations I am running are all single threaded so I want to be able to launch as many instances of the simulation as cores I have available across multiple computer systems.

* Step 1:
  * Run EBIT Charge Breeding Simulator
  * This outputs a single file containing many macro definitions with headers and footers such as :
```
# START: E:Sb,Z:51,A:129,Q:41:T:0.800002
/pga/selectGunAction 1
/gps/particle ion
/gps/ion 51 129 41
/gps/position 0 0 0
/gps/ene/mono 0
/histo/filename E:Sb,Z:51,A:129,Q:41:T:0.800002
/run/beamOn 111147
# END
# START: E:Sb,Z:51,A:129,Q:41:T:1.000001
/pga/selectGunAction 1
/gps/particle ion
/gps/ion 51 129 41
/gps/position 0 0 0
/gps/ene/mono 0
/histo/filename E:Sb,Z:51,A:129,Q:41:T:1.000001
/run/beamOn 111147
# END
```
  * Typically there will be a large number of these entries.  
  * I simplify my life by having the header (everything past # START) be the same as my filenames I will use throughout with just different file extensions

* Step 2:
  * Configure Geant4ClusterMacroRunner with all systems available to you and modify local_system_execution.sh and remote_system_execution.sh to meet your needs.  I will hopefully go more in depth on these later in this document.

* Step 3: Profit?!?!
  * Sadly no, this is physics, we don't do that.  
  * Run pysched.py (Python Scheduler.. I know, I need a better name)
  * This will read in the above style macro file and create a list of G4MacroRun objects, each object containing the header minus the '# START' part and the body of the macro
  * The scheduler will then create a macro file for each individual macro as it goes, store those in the local work directory you define in the config file 'work_dir = ', scp those to the remote temp directory on the system it will attempt to run the GEANT4 macro on.  Then it will, in my case, run a docker instance which runs the macro against my GEANT4 simulation.
  * This simulation then outputs a root file which this scheduler (this program) picks up and returns to the work_dir.

If something fails in step 3 the program doesn't care.  It logs everything to logfile.stdout_stderr located in the 'work_dir' and just does what it can.  If something fails the idea is to either not care or to run it again.  If you run the scheduler again it looks in the 'work_dir' for .root files, if they exist it skips over that macro and only loads in the macros for which the .root files do not exist.  I am write something to re-run failed jobs at some point but for right now I just re-run the software.  

## Docker instance

For my simulations I made and pushed to docker hub a docker container that contains ROOT6 and Geant4.  I will be skipping some steps on how I setup docker so you should read some intro to docker documentation.  The idea behind it though is that you can create a very lightweight container that contains an installation of GEANT4 and ROOT6 along with a mostly complete Ubuntu 18 environment.  This allows me to run this on any Linux/MacOS system I have access to that has docker installed without having to configure ROOT & GEANT4 on each system.  Building the initial docker instance located at [GEANT4 & ROOT6 Docker instance](https://hub.docker.com/repository/docker/bobskr/decayspec-geant4-baseimg) looked somewhat as follows.

*  Install Docker  
*  Instantiate a Ubuntu instance and start a shell in it:
```
docker run --name decayspec-geant4 -it ubuntu:latest bash
```
*  Inside the docker container where you should be now I did the following to install ROOT 6.14.06

STEP 1:  Install dev environment so we can compile ROOT6
```
apt update
apt upgrade
apt install wget git dpkg-dev cmake g++ gcc binutils libx11-dev libxpm-dev \
libxft-dev libxext-dev gfortran libssl-dev libpcre3-dev \
xlibmesa-glu-dev libglew1.5-dev libftgl-dev \
libmysqlclient-dev libfftw3-dev libcfitsio-dev \
graphviz-dev libavahi-compat-libdnssd-dev \
libldap2-dev python-dev libxml2-dev libkrb5-dev \
libgsl0-dev libqt4-dev
```
STEP2 : Download ROOT6
```
cd /usr/local/src
wget https://root.cern.ch/download/root_v6.14.06.source.tar.gz
tar xvf root_v6.14.06.source.tar.gz
mkdir buildroot
cd buildroot
```
STEP3 : Compile and install ROOT6 in /usr/local/root/root-6.14.06
```
cmake -DCMAKE_INSTALL_PREFIX=/usr/local/root/root-6.14.06 -Dminuit2=ON -Dxml=ON -Dmathmore=ON ../root-6.14.06
cmake --build . -- -j5
make install
```

*  Now we need to install GEANT4 inside the docker instances

STEP 1 : Download depenencies, there are probably some overlaps here but whatever
```
apt-get install libxerces-c-dev qt4-dev-tools freeglut3-dev libmotif-dev tk-dev cmake libxpm-dev libxmu-dev libxi-dev
```
STEP 2 : Download version 10.05.p01 or whatever your poison from [Geant4 Downloads](http://geant4.web.cern.ch/support/download_archive) and copy this into the docker instance via `docker cp` command into the /usr/local/src directory.  Once copied in there unpack it and make a build directory.

```
cd /usr/local/src
tar xvf geant4.10.05.p01.tar.gz
mkdir buildgeant4
cd buildgeant4
```
STEP 3 : Build and install GEANT4
```
cmake -DCMAKE_INSTALL_PREFIX=/usr/local/geant4/geant4.10.05.p01 -DCMAKE_BUILD_TYPE=Release -DGEANT4_INSTALL_DATA=ON -DGEANT4_USE_QT=ON -DGEANT4_USE_OPENGL_X11=ON -DGEANT4_USE_GDML=ON -DGEANT4_USE_RAYTRACER_X11=ON -DGEANT4_USE_NETWORKDAWN=ON -DGEANT4_BUILD_EXAMPLES=OFF -DGEANT4_BUILD_MULTITHREADED=ON ../geant4.10.05.p01
make -j2
make install
```
  * From there I had docker create an image for this and pushed it up to the docker hub.
  * I can now create a docker layer that contains my GEANT4 simulation so I can change this easily between runs.  I use the following Dockerfile to do so check out the most recent code base from github and compile it.

Dockerfile:
```
FROM bobskr/decayspec-geant4-baseimg
WORKDIR /tmp
RUN git clone https://github.com/TITANCollaboration/decayspec_8pi_geant4sim.git
COPY *.cc /tmp/decayspec_8pi_geant4sim/src/
RUN mkdir build
RUN /bin/bash -c "source /usr/local/geant4/geant4.10.05.p01/bin/geant4.sh && source /usr/local/root/root-6.14.06/bin/thisroot.sh && cd build && cmake ../decayspec_8pi_geant4sim && make -j4 && make install"
COPY runEBIT.sh /usr/local/bin
ENTRYPOINT ["runEBIT.sh"]
```

runEBIT.sh :
```
#!/bin/bash
cd /mydata
source /usr/local/geant4/geant4.10.05.p01/bin/geant4.sh
source /usr/local/root/root-6.14.06/bin/thisroot.sh
/tmp/build/ebit $@
```
Given the Dockerfile and runEBIT.sh above you can build the new image on each system you will be running them on via :
```
docker build -t decayspec-geant4-working .
```

## Running the software

After all that you can just run this program such as :

```
python ./pysched.py --configFile myconfig.cfg
```
It should run the specified number of instances on each machine and report back as they are completed putting all the relevant data into your 'work_dir'.
