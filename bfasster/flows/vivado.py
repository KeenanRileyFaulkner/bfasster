"""Flow to create Vivado synthesis and implementation ninja snippets."""
from argparse import ArgumentParser
import chevron
import json
from bfasster.paths import (
    DESIGNS_PATH,
    IMPL_TOOLS_PATH,
    NINJA_BUILD_PATH,
    ROOT_PATH,
    SYNTH_TOOLS_PATH,
    TOOLS_PATH,
    UTILS_PATH,
    FLOWS_PATH,
    VIVADO_RULES_PATH,
)
from bfasster.utils import compare_json, only_once
from bfasster.yaml_parser import YamlParser


class Vivado:
    """Flow to create Vivado synthesis and implementation ninja snippets."""

    def __init__(self, design, ooc=False):
        self.design = DESIGNS_PATH / design

        self.ooc = ooc
        if ooc:
            self.build = ROOT_PATH / "build" / design / "ooc"
        else:
            self.build = ROOT_PATH / "build" / design / "in_context"
        self.synth_output = self.build / "synth"
        self.impl_output = self.build / "impl"
        self.__create_build_dirs()

        self.top = YamlParser(self.design / "design.yaml").parse_top_module()
        self.__read_hdl_files()

        self.part = "xc7a200tlffg1156-2L"

    def __create_build_dirs(self):
        self.build.mkdir(parents=True, exist_ok=True)
        self.synth_output.mkdir(exist_ok=True)
        self.impl_output.mkdir(exist_ok=True)

    def __read_hdl_files(self):
        """Read the hdl files in the design directory"""
        self.v = []
        self.sv = []
        for child in self.design.rglob("*"):
            if child.is_dir():
                continue

            if child.suffix == ".v":
                self.v.append(str(child))
            elif child.suffix == ".sv":
                self.sv.append(str(child))

    def create(self):
        self.__create_rule_snippets()
        self.__write_json_files()
        self.__create_build_snippets()

    @only_once
    def __create_rule_snippets(self):
        with open(VIVADO_RULES_PATH, "r") as f:
            vivado_ninja = chevron.render(
                f,
                {
                    "utils": str(UTILS_PATH),
                },
            )
        with open(NINJA_BUILD_PATH, "a") as f:
            f.write(vivado_ninja)

    def __write_json_files(self):
        self.__write_synth_json()
        self.__write_impl_json()

    def __write_synth_json(self):
        """Specify synthesis arguments in a json file that chevron will use to fill in the tcl template"""
        synth = {
            "part": self.part,
            "verilog": self.v,
            "system_verilog": self.sv,
            "top": self.top,
            "edif": "viv_synth.edif",
            "dcp": "synth.dcp",
            "io": str(self.synth_output / "iofile.txt") if not self.ooc else False,
            "synth_output": str(self.synth_output),
        }
        synth_json = json.dumps(synth, indent=4)

        # check if the synth json file already exists and compare it to what we're about to write
        json_equivalent = compare_json(self.synth_output / "synth.json", synth_json)

        if not json_equivalent:
            with open(self.synth_output / "synth.json", "w") as f:
                f.write(synth_json)

    def __write_impl_json(self):
        """Specify implementation arguments in a json file that chevron will use to fill in the tcl template"""
        impl = {
            "synth_edif": "viv_synth.edif",
            "part": self.part,
            "xdc": str(self.synth_output / (self.top + ".xdc"))
            if not self.ooc
            else False,
            "dcp": "impl.dcp",
            "impl_edif": "viv_impl.edif",
            "netlist": "viv_impl.v",
            "util_file": "utilization.txt",
            "bit": str(self.impl_output / (self.top + ".bit"))
            if not self.ooc
            else False,
            "impl_output": str(self.impl_output),
            "synth_output": str(self.synth_output),
        }
        impl_json = json.dumps(impl, indent=4)

        # check if the impl json file already exists and compare it to what we're about to write
        json_equivalent = compare_json(self.impl_output / "impl.json", impl_json)

        if not json_equivalent:
            with open(self.impl_output / "impl.json", "w") as f:
                f.write(impl_json)

    def __create_build_snippets(self):
        self.__create_synth_ninja()
        self.__create_impl_ninja()

    def __create_synth_ninja(self):
        """Create ninja snippets for vivado synthesis in build.ninja"""
        with open(TOOLS_PATH / "synth" / "viv_synth.ninja.mustache") as f:
            synth_ninja = chevron.render(
                f,
                {
                    "in_context": not self.ooc,
                    "synth_output": str(self.synth_output),
                    "json": str(self.synth_output / "synth.json"),
                    "utils": str(UTILS_PATH),
                    "synth_library": SYNTH_TOOLS_PATH,
                    "top": self.top,
                    "verilog": self.v,
                    "system_verilog": self.sv,
                },
            )

        with open(NINJA_BUILD_PATH, "a") as f:
            f.write(synth_ninja)

    def __create_impl_ninja(self):
        """Create ninja snippets for vivado implementation in build.ninja"""
        with open(TOOLS_PATH / "impl" / "viv_impl.ninja.mustache") as f:
            impl_ninja = chevron.render(
                f,
                {
                    "in_context": not self.ooc,
                    "impl_output": str(self.impl_output),
                    "synth_output": str(self.synth_output),
                    "json": str(self.impl_output / "impl.json"),
                    "impl_library": IMPL_TOOLS_PATH,
                    "synth_edif": "viv_synth.edif",
                    "top": self.top,
                },
            )

        with open(NINJA_BUILD_PATH, "a") as f:
            f.write(impl_ninja)

    @only_once
    def add_ninja_deps(self, deps=[]):
        """Add dependencies to the master ninja file that would cause it to rebuild if modified"""
        deps.append(f"{TOOLS_PATH}/synth/viv_synth.ninja.mustache ")
        deps.append(f"{TOOLS_PATH}/impl/viv_impl.ninja.mustache ")
        deps.append(f"{FLOWS_PATH}/vivado.py ")
        deps.append(f"{VIVADO_RULES_PATH}\n")

        return deps

    def get_top_level_flow_path(self):
        return str(FLOWS_PATH / "vivado.py")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--design", type=str, help="Design to run")
    args = parser.parse_args()
    Vivado(args.design).create()
