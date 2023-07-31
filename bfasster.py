from argparse import ArgumentParser
import pathlib
import subprocess
from bfasster.flows.flow import get_flow
from bfasster.yaml_parser import YamlParser
from bfasster.utils import error
from bfasster.paths import ROOT_PATH, DESIGNS_PATH
import chevron


class ApplicationRunner:
    def run(self, args):
        # save the flow and design paths
        self.parse_args(args)

        # run the flows to create the ninja files
        for flow in self.flows:
            flow.create()

        # populate the master ninja template
        self.create_master_ninja()

        # run the build.ninja file
        self.run_ninja()

    def parse_args(self, args):
        if args.yaml:
            parser = YamlParser(args.yaml)
            parser.parse()
            self.designs = parser.design_paths
            self.flows = parser.flows
        else:
            design = DESIGNS_PATH / args.design
            self.designs = [str(design)]
            self.flows = [get_flow(args.flow)(str(design).split("/")[-1])]

    def create_master_ninja(self):
        master_ninja = self.populate_template()

        with open(ROOT_PATH / "build.ninja", "w") as f:
            f.write(master_ninja)

    def populate_template(self):
        with open(ROOT_PATH / "master.ninja.mustache") as f:
            master_ninja = chevron.render(
                f,
                {
                    "design_dir": self.designs,
                },
            )

        return master_ninja

    def run_ninja(self):
        subprocess.Popen("ninja", cwd=ROOT_PATH)


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
    args = parser.parse_args()

    check_args(args)
    ApplicationRunner().run(args)
