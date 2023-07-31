"""Script to run a flow on one or more designs."""
from argparse import ArgumentParser
import pathlib
import subprocess
from bfasster.flows.flow_utils import get_flow
from bfasster.yaml_parser import YamlParser
from bfasster.utils import error
from bfasster.paths import ROOT_PATH, DESIGNS_PATH
import chevron


class ApplicationRunner:
    """Runs a given flow on one or more designs using Ninja."""

    def run(self, args):
        """Run a flow on one or more designs."""

        # save the flow and design paths
        self.__parse_args(args)

        # run the flows to create the ninja files
        for flow in self.flows:
            flow.create()

        # populate the master ninja template
        self.__create_master_ninja()

        # run the build.ninja file
        self.__run_ninja()

    def __parse_args(self, args):
        if args.yaml:
            parser = YamlParser(args.yaml)
            parser.parse_design_flow()
            self.designs = parser.design_paths
            self.flows = parser.flows
        else:
            self.designs = [str(DESIGNS_PATH / args.design)]
            self.flows = [get_flow(args.flow)(args.design)]

    def __create_master_ninja(self):
        master_ninja = self.__populate_template()

        with open(ROOT_PATH / "build.ninja", "w") as f:
            f.write(master_ninja)

    def __populate_template(self):
        with open(ROOT_PATH / "master.ninja.mustache") as f:
            master_ninja = chevron.render(
                f,
                {
                    "design_dir": self.designs,
                },
            )

        return master_ninja

    def __run_ninja(self):
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
        "--design", type=str, help="Design directory for single design flows"
    )
    parser.add_argument("--flow", type=str, help="Flow to run for single design flows")
    args = parser.parse_args()

    check_args(args)
    ApplicationRunner().run(args)
