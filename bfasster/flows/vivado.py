"""Flow to create Vivado synthesis and implementation ninja snippets."""
from argparse import ArgumentParser
import chevron
import json
from bfasster.paths import (
    DESIGNS_PATH,
    BFASSTER_PATH,
    TOOLS_PATH,
    UTILS_PATH,
    FLOWS_PATH,
)
from bfasster.yaml_parser import YamlParser


class Vivado:
    """Flow to create Vivado synthesis and implementation ninja snippets."""

    def __init__(self, design):
        self.design = DESIGNS_PATH / design
        self.output = self.design / "out"
        self.__create_output_dir()

        self.top = YamlParser(self.design / "design.yaml").parse_top_module()
        self.__read_hdl_files()

        self.part = "xc7a100tcsg324-1"

        self.vivado_library = TOOLS_PATH / "vivado"
        self.__create_vivado_ninja()
        self.synth_library = TOOLS_PATH / "synth"
        self.impl_library = TOOLS_PATH / "impl"

    def __create_output_dir(self):
        self.output.mkdir(parents=True, exist_ok=True)

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

    def __create_vivado_ninja(self):
        with open(self.vivado_library / "vivado.ninja.mustache", "r") as f:
            vivado_ninja = chevron.render(
                f,
                {
                    "utils": str(UTILS_PATH),
                },
            )
        with open(self.output / "build.ninja", "w") as f:
            f.write(vivado_ninja)

    def create(self):
        self.__write_json_files()
        self.__create_ninja_files()

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
            "io": "iofile.txt",
        }
        synth_json = json.dumps(synth, indent=4)
        with open(self.output / "synth.json", "w") as f:
            f.write(synth_json)

    def __write_impl_json(self):
        """Specify implementation arguments in a json file that chevron will use to fill in the tcl template"""
        impl = {
            "synth_edif": "viv_synth.edif",
            "part": self.part,
            "xdc": self.top + ".xdc",
            "dcp": "impl.dcp",
            "impl_edif": "viv_impl.edif",
            "netlist": "viv_impl.v",
            "util_file": "utilization.txt",
            "bit": self.top + ".bit",
        }
        impl_json = json.dumps(impl, indent=4)
        with open(self.output / "impl.json", "w") as f:
            f.write(impl_json)

    def __create_ninja_files(self):
        self.__create_synth_ninja()
        self.__create_impl_ninja()
        self.__create_master_ninja()

    def __create_synth_ninja(self):
        """Create ninja snippets for vivado synthesis in build.ninja"""
        with open(TOOLS_PATH / "synth" / "viv_synth.ninja.mustache") as f:
            synth_ninja = chevron.render(
                f,
                {
                    "json": str(self.output / "synth.json"),
                    "utils": str(UTILS_PATH),
                    "synth_library": self.synth_library,
                    "top": self.top,
                    "verilog": self.v,
                    "system_verilog": self.sv,
                },
            )

        with open(self.output / "build.ninja", "a") as f:
            f.write(synth_ninja)

    def __create_impl_ninja(self):
        """Create ninja snippets for vivado implementation in build.ninja"""
        with open(TOOLS_PATH / "impl" / "viv_impl.ninja.mustache") as f:
            impl_ninja = chevron.render(
                f,
                {
                    "json": str(self.output / "impl.json"),
                    "impl_library": self.impl_library,
                    "synth_edif": "viv_synth.edif",
                    "top": self.top,
                },
            )

        with open(self.output / "build.ninja", "a") as f:
            f.write(impl_ninja)

    def __create_master_ninja(self):
        """Create the top level ninja file that will run the synthesis and implementation ninja files"""
        with open(self.output / "build.ninja", "a") as f:
            f.write("rule configure\n")
            f.write(f"    command = python {BFASSTER_PATH}/flows/vivado.py\n")
            f.write("    generator = 1\n\n")
            f.write("build build.ninja: configure ")
            f.write(f"{TOOLS_PATH}/synth/viv_synth.ninja.mustache ")
            f.write(f"{TOOLS_PATH}/impl/viv_impl.ninja.mustache ")
            f.write(f"{FLOWS_PATH}/vivado.py ")
            f.write(f"{self.vivado_library}/vivado.ninja\n")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--design", type=str, help="Design to run")
    args = parser.parse_args()
    Vivado(args.design).create()
