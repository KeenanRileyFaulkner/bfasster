import pathlib
import subprocess
from bfasster.flows.flow import get_flow


class ApplicationRunner:
    def __init__(self):
        self.root = pathlib.Path(__file__).parent

    def run(self):
        # create and execute a yaml parser
        self.design = "add4"
        flow = "vivado"

        # run the flow
        flow = get_flow(flow)()
        flow.create()

        # run the ninja file
        self.run_ninja()

    def run_ninja(self):
        subprocess.Popen("ninja", cwd=self.root / "designs" / self.design / "out")


if __name__ == "__main__":
    ApplicationRunner().run()
