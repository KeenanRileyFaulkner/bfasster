"""Parse a yaml file to obtain a flow and a list of target designs"""
import pathlib
import yaml
from bfasster.flows.flow_utils import get_flow
from bfasster.utils import error
from bfasster import paths


class YamlParser:
    """Parses a yaml file to obtain a flow and list of target designs"""

    def __init__(self, yaml_path):
        self.yaml_path = yaml_path

    def parse_design_flow(self):
        """Parse a yaml file into design paths and an instance of the specified flow for each design"""
        self.experiment_props = None
        self.__read_experiment_yaml()
        self.__check_experiment_props_for_yaml()

        self.post_run = None
        self.__check_for_post_run()

        self.design_paths = []
        self.__collect_design_paths()
        self.__uniquify_design_paths()

        self.flows = []
        self.__create_flows()

    def __read_experiment_yaml(self):
        with open(self.yaml_path) as f:
            self.experiment_props = yaml.safe_load(f)

    def __check_experiment_props_for_yaml(self):
        if "flow" not in self.experiment_props:
            error(f"Experiment {self.yaml_path} does not specify a flow")

    def __check_for_post_run(self):
        if "post_run" in self.experiment_props:
            self.post_run = getattr(self, self.experiment_props("post_run"))

    def __collect_design_paths(self):
        """Get all designs from the config yaml"""

        if "designs" in self.experiment_props:
            for design in self.experiment_props.pop("designs"):
                design_path = paths.DESIGNS_PATH / design
                if not design_path.is_dir():
                    error("Provided design directory", design_path, "does not exist")

                # Check if provided directory contains a design
                if (design_path / "design.yaml").is_file():
                    self.design_paths.append(str(design_path))
                    continue

                for design_child in design_path.rglob("*"):
                    if not design_child.is_dir():
                        continue

                    if (design_child / "design.yaml").is_file():
                        self.design_paths.append(str(design_child))
                        continue

        if "design_dirs" in self.experiment_props:
            for design_dir in self.experiment_props.pop("design_dirs"):
                design_dir_path = paths.DESIGNS_PATH / design_dir
                if not design_dir_path.is_dir():
                    error(f"{design_dir_path} is not a directory")

                for dir_item in design_dir_path.iterdir():
                    item_path = design_dir_path / dir_item
                    if item_path.is_dir():
                        self.design_paths.append(
                            pathlib.Path(design_dir) / dir_item.name
                        )

    def __uniquify_design_paths(self):
        self.design_paths = list(set(self.design_paths))
        self.design_paths.sort()

    def __create_flows(self):
        for design in self.design_paths:
            design = str(design)
            design_basename = "/".join(design.split("/")[-2:])
            flow = get_flow(self.experiment_props["flow"])(design_basename)
            self.flows.append(flow)

    def parse_top_module(self):
        """Parse a yaml file to obtain a top module"""
        self.experiment_props = None
        self.__read_experiment_yaml()
        return self.__check_for_top()

    def __check_for_top(self):
        if "top" not in self.experiment_props:
            error(f"Experiment {self.yaml_path} does not specify a top module")
        return self.experiment_props["top"]
