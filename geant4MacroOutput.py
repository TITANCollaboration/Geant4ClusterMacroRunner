def geant4MacroOutput(macro_filename, energy, particle_num):

    # Open the macro file for writing, we should overwrite for now..
    with open(macro_filename, 'a') as geantMacroFile:
        # Write header before each line of beam run macro info so we can split this up easily later
        geantMacroFile.write("# START: E:%i\n" % energy)
        geantMacroFile.write("/pga/selectGunAction 1\n")
        geantMacroFile.write("/gps/particle gamma\n")
        geantMacroFile.write("/gps/position 0 0 0\n")
        geantMacroFile.write("/gps/energy %i keV\n" % energy)
        geantMacroFile.write("/gps/ang/type iso\n")
        geantMacroFile.write("/histo/filename E:%i\n" % energy)
        geantMacroFile.write("/run/beamOn %i\n" % (particle_num))
        # geantMacroFile.write("/run/beamOn %i\n" % (outputConfig.eventsPerTimeSlice * mySpecies.results[chargeStateResults][myrow][1]))
        geantMacroFile.write("# END\n")
    # geantMacroFile.write("")

    return 0
