"""Flow to create Vivado synthesis and implementation ninja snippets."""
from argparse import ArgumentParser
import pathlib
import chevron
import json
import shutil
from bfasster.paths import (
    DESIGNS_PATH,
    BFASSTER_PATH,
    TOOLS_PATH,
    UTILS_PATH,
    FLOWS_PATH,
)


class Vivado:
    """Flow to create Vivado synthesis and implementation ninja snippets."""

    def __init__(self, design):
        self.design = DESIGNS_PATH / design
        self.output = self.design / "out"
        self.create_output_dir()

        self.top = design.split("/")[-1]
        self.v = [str(self.design / f"{str(design).split('/')[-1]}.v")]
        self.sv = None

        self.part = "xc7a100tcsg324-1"

        self.vivado_library = TOOLS_PATH / "vivado"
        self.copy_vivado_ninja()
        self.synth_library = TOOLS_PATH / "synth"
        self.impl_library = TOOLS_PATH / "impl"

    def create_output_dir(self):
        self.output.mkdir(parents=True, exist_ok=True)

    def copy_vivado_ninja(self):
        vivado_ninja = self.vivado_library / "vivado.ninja"
        master_ninja = self.output / "build.ninja"
        shutil.copy(vivado_ninja, master_ninja)

    def create(self):
        self.write_json_files()
        self.create_ninja_files()

    def write_json_files(self):
        self.write_synth_json()
        self.write_impl_json()

    def write_synth_json(self):
        """Specify synthesis arguments in a json file that chevron will use to fill in the tcl template"""
        synth = {
            "part": self.part,
            "verilog": self.v,
            "top": self.top,
            "edif": "viv_synth.edif",
            "dcp": "synth.dcp",
            "io": "iofile.txt",
        }
        synth_json = json.dumps(synth, indent=4)
        with open(self.output / "synth.json", "w") as f:
            f.write(synth_json)

    def write_impl_json(self):
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

    def create_ninja_files(self):
        self.create_synth_ninja()
        self.create_impl_ninja()
        self.create_master_ninja()

    def create_synth_ninja(self):
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

    def create_impl_ninja(self):
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

    def create_master_ninja(self):
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
