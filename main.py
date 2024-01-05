import sys
from typing import Literal

from FUWS.FUWS import FUWS
from Parameters.UserDefined import UserDefined
from Parameters.Variable import Variable
from UWSInc.uWSInc import uWSInc
from UWSIncPlus.uWSIncPlus import uWSIncPlus
from UWSWindow.uWSWindow import uWSWindow

if __name__ == "__main__":
    # initialize user given parameters by default values.
    UserDefined.min_sup = 0.2
    UserDefined.wgt_factor = 1.0
    Variable.mu = 0.70

    # Select the algorithm based on command line input

    algorithm: Literal["FUWS", "UWSInc", "UWSIncPlus", "UWSWindow"] = (
        "FUWS"
        if len(sys.argv) <= 1 or sys.argv[1] == "FUWS"
        else "UWSInc"
        if sys.argv[1] == "UWSInc"
        else "UWSIncPlus"
        if sys.argv[1] == "UWSIncPlus"
        else "UWSWindow"
    )

    if algorithm == "FUWS":
        FUWS("Files/input.txt", "Files/manual_weights.txt", "Files/result")
    elif algorithm == "UWSInc":
        uWSInc(
            "Files/input.txt",
            ["Files/inc_1.txt", "Files/inc_2.txt"],
            "Files/manual_weights.txt",
            "Files/result",
        )
    elif algorithm == "UWSIncPlus":
        uWSIncPlus(
            "Files/input.txt",
            ["Files/inc_1.txt", "Files/inc_2.txt"],
            "Files/manual_weights.txt",
            "Files/result",
        )
    elif algorithm == "UWSWindow":
        uWSWindow(
            ["Files/input.txt", "Files/inc_1.txt", "Files/inc_2.txt"],
            "Files/manual_weights.txt",
            "Files/result",
            UserDefined.min_sup,
            UserDefined.wgt_factor,
            Variable.mu,
            100000000,
        )
