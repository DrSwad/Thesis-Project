import sys
from typing import Literal

from FUWS.FUWS import FUWS
from Parameters.UserDefined import UserDefined
from Parameters.Variable import Variable
from UWSInc.uWSInc import uWSInc
from UWSIncPlus.uWSIncPlus import uWSIncPlus
from UWSWindow.uWSWindow import uWSWindow

if __name__ == "__main__":
    # Select the algorithm and parameters based on command line input
    assert len(sys.argv) >= 6
    algo_name = sys.argv[1]
    UserDefined.min_sup = float(sys.argv[2])
    UserDefined.wgt_factor = float(sys.argv[3])
    Variable.mu = float(sys.argv[4])
    input_file_name = sys.argv[5]
    inc_file_names = sys.argv[6:]

    algorithm: Literal["FUWS", "UWSInc", "UWSIncPlus", "UWSWindow"] = (
        "FUWS"
        if algo_name == "FUWS"
        else "UWSInc"
        if algo_name == "UWSInc"
        else "UWSIncPlus"
        if algo_name == "UWSIncPlus"
        else "UWSWindow"
    )

    if algorithm == "FUWS":
        # FUWS("Files/input.txt", "Files/manual_weights.txt", "Files/result")
        FUWS(input_file_name, "Files/weights.csv", "Files/result")
    elif algorithm == "UWSInc":
        uWSInc(
            input_file_name,
            inc_file_names,
            "Files/weights.txt",
            "Files/result",
        )
    elif algorithm == "UWSIncPlus":
        uWSIncPlus(
            input_file_name,
            inc_file_names,
            "Files/weights.txt",
            "Files/result",
        )
    elif algorithm == "UWSWindow":
        uWSWindow(
            [input_file_name] + inc_file_names,
            "Files/weights.csv",
            "Files/result",
            UserDefined.min_sup,
            UserDefined.wgt_factor,
            Variable.mu,
            100000000,
        )
