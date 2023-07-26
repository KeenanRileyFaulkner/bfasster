from argparse import ArgumentParser
import pathlib
import subprocess
from bfasster.yaml_parser import YamlParser
from bfasster.utils import error
import chevron


class ApplicationRunner:
    def __init__(self):
        self.root = pathlib.Path(__file__).parent

    def run(self, args):
        # create and execute a yaml parser
        if args.yaml:
            parser = YamlParser(args.yaml)
            parser.parse()
            self.designs = parser.design_paths
            self.flows = parser.flows
        else:
            self.designs = [args.design]
            self.flows = [args.flow]

        # run the flows to create the ninja files
        for flow in self.flows:
            flow.create()

        # populate the master ninja template
        with open(self.root / "master.ninja.mustache") as f:
            master_ninja = chevron.render(
                f,
                {
                    "design_dir": self.designs,
                },
            )

        with open(self.root / "build.ninja", "w") as f:
            f.write(master_ninja)

        # run the build.ninja file
        self.run_ninja()

    def run_ninja(self):
        subprocess.Popen("ninja", cwd=self.root)


def check_args(args):
    if args.yaml and (args.design or args.flow):
        error("Cannot specify both a yaml file and a design/flow")
    elif not args.yaml and not (args.design and args.flow):
        error("Must specify either a yaml file or a design/flow")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--yaml", type=pathlib.Path, help="Yaml file with flow specs")
    parser.add_argument(
        "--design", type=pathlib.Path, help="Design directory for single design flows"
    )
    parser.add_argument("--flow", type=str, help="Flow to run for single design flows")
    parser.add_argument(
        "-j", "--threads", type=int, default=1, help="Number of threads"
    )
    args = parser.parse_args()

    check_args(args)
    ApplicationRunner().run(args)
