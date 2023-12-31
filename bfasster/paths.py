""" Repository paths using pathlib """

import pathlib
import os

ROOT_PATH = pathlib.Path(__file__).resolve().parent.parent

DESIGNS_PATH = ROOT_PATH / "designs"
BFASSTER_PATH = ROOT_PATH / "bfasster"
EXPERIMENTS_PATH = ROOT_PATH / "experiments"
RESOURCES_PATH = ROOT_PATH / "resources"
SCRIPTS_PATH = ROOT_PATH / "scripts"
ERROR_FLOW_PATH = ROOT_PATH / "error_flows"
THIRD_PARTY_PATH = ROOT_PATH / "third_party"

TOOLS_PATH = BFASSTER_PATH / "tools"
UTILS_PATH = BFASSTER_PATH / "bin"
FLOWS_PATH = BFASSTER_PATH / "flows"

SYNTH_TOOLS_PATH = TOOLS_PATH / "synth"
IMPL_TOOLS_PATH = TOOLS_PATH / "impl"
VIVADO_RULES_PATH = TOOLS_PATH / "vivado" / "vivado.ninja.mustache"

NINJA_BUILD_PATH = ROOT_PATH / "build.ninja"

I2C_RESOURCES = RESOURCES_PATH / "iCEcube2"
YOSYS_RESOURCES = RESOURCES_PATH / "yosys"
ONESPIN_RESOURCES = RESOURCES_PATH / "onespin"

YOSYS_INSTALL_DIR = THIRD_PARTY_PATH / "yosys"


def get_fasm2bels_path():
    if "BFASST_PATH_FASM2BELS" in os.environ:
        return pathlib.Path(os.environ["BFASST_PATH_FASM2BELS"])
    return THIRD_PARTY_PATH / "fasm2bels"
