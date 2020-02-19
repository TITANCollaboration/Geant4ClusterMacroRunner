#  We want to read in the output of the EBIT sims generated G4 Macro and break it up
#  into an array of classes
import os

class G4MacroRun:
    # Class : G4MacroRun
    # Store each macro process to later be executed in parallel, the header is just the START line
    # The block is everything else
    # status = is it done? has it started? did it fail?  you get the idea..
    # Macro file format below :
    # -----
    # # START: E:Sb,Z:51,A:129,Q:40:T:0.400002
    # /pga/selectGunAction 1
    # /gps/particle ion
    # /gps/ion 51 129 40
    # /gps/position 0 0 0
    # /gps/ene/mono 0
    # /histo/filename E_Sb_Z_51_A_129_Q_40_T_0.400002
    # /run/beamOn 20000
    # -----

    def __init__(self, header, macro_block, g4id, status=None):
        self.header = header
        self.macro_block = macro_block
        self.status = status
        self.g4id = g4id


def read_in_geant4_macro_file(g4_macro_filename):
    list_of_macro_objects = []
    macro_line_buffer = ""
    macro_header = ""
    macro_block = ""
    g4id = 0

    with open(g4_macro_filename) as g4_file:
        for g4_file_line in g4_file:
            if '# START' in g4_file_line:
                macro_header = g4_file_line
            elif '# END' in g4_file_line:
                # WRITE OBJECT
                list_of_macro_objects.append(G4MacroRun(macro_header.rstrip()[9:], macro_block, g4id, 0))
                g4id = g4id + 1
                macro_block = ""  # Setup for next block
            else:
                macro_block += g4_file_line
    return list_of_macro_objects  # fix me later
