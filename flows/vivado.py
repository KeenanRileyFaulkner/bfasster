"""Flow to create Vivado synthesis and implementation ninja snippets."""
import pathlib
import chevron
import json
import shutil


class Vivado:
    """Flow to create Vivado synthesis and implementation ninja snippets."""

    def __init__(self):
        self.root = pathlib.Path(__file__).parent.parent

        self.design = self.root / "designs" / "add4"
        self.output = self.design / "out"
        self.create_output_dir()

        self.top = "add4"
        self.v = [str(self.design / "add4.v")]
        self.sv = None

        self.part = "xc7a100tcsg324-1"

        self.utils = self.root / "bin"

        self.vivado_library = self.root / "tools" / "vivado"
        self.copy_vivado_ninja()
        self.synth_library = self.root / "tools" / "synth"
        self.impl_library = self.root / "tools" / "impl"

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
        with open(self.root / "tools" / "synth" / "viv_synth.ninja.mustache") as f:
            synth_ninja = chevron.render(
                f,
                {
                    "json": str(self.output / "synth.json"),
                    "utils": self.utils,
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
        with open(self.root / "tools" / "impl" / "viv_impl.ninja.mustache") as f:
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
            f.write(f"    command = python {self.root}/flows/vivado.py\n")
            f.write("    generator = 1\n\n")
            f.write("build build.ninja: configure ")
            f.write(f"{self.root}/tools/synth/viv_synth.ninja.mustache ")
            f.write(f"{self.root}/tools/impl/viv_impl.ninja.mustache ")
            f.write(f"{self.root}/flows/vivado.py ")
            f.write(f"{self.vivado_library}/vivado.ninja\n")


if __name__ == "__main__":
    Vivado().create()
