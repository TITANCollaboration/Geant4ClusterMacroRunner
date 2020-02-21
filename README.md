# Geant4ClusterMacroRunner

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
