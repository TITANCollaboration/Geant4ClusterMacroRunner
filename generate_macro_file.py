import argparse
from geant4MacroOutput import geant4MacroOutput


def generate_macro_file(args):
    for run_energy in range(int(args.init_energy), int(args.final_energy), int(args.step_size)):
        print("Run energy %i" % run_energy)
        geant4MacroOutput(args.output_file, run_energy, int(args.event_num))



def main():

    parser = argparse.ArgumentParser(description='Geant4 Macro Generator')

    parser.add_argument('--output_file', dest='output_file', required=False,
                        help="Specify the complete path to the macro file, by default we'll use g4macro_file.mac")

    parser.add_argument('--init_energy', dest='init_energy', required=False,
                        help="Initial energy (keV)")
    parser.add_argument('--final_energy', dest='final_energy', required=False,
                        help="Final energy (keV)")
    parser.add_argument('--step_size', dest='step_size', required=False,
                        help="Step size (keV)")
    parser.add_argument('--event_num', dest='event_num', required=False,
                        help="Number of events per energy")
    parser.set_defaults(output_file="g4macro_file.mac")

    args, unknown = parser.parse_known_args()
    generate_macro_file(args)

if __name__ == "__main__":
    main()
