FROM bobskr/decayspec-geant4-baseimg
WORKDIR /tmp
RUN git clone https://github.com/TITANCollaboration/decayspec_8pi_geant4sim.git
COPY *.cc /tmp/decayspec_8pi_geant4sim/src/
RUN mkdir build
RUN /bin/bash -c "source /usr/local/geant4/geant4.10.05.p01/bin/geant4.sh && source /usr/local/root/root-6.14.06/bin/thisroot.sh && cd build && cmake ../decayspec_8pi_geant4sim && make -j4 && make install"
COPY runEBIT.sh /usr/local/bin
ENTRYPOINT ["runEBIT.sh"]
