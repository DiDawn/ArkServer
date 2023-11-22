import os
import csv
from dataclasses import dataclass


def extract():
    params = {}
    if os.path.exists("params.csv"):
        with open("params.csv", encoding="utf8", newline="") as f:
            data = csv.reader(f)
            for line in data:
                params[line[0]] = line[1]
    else:
        with open("params.csv", encoding="utf8", newline="") as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(["pathToShooterGame", "None"])
            writer.writerow(["serverPort", "None"])
            writer.writerow(["targetPort", "None"])
            writer.writerow(["targetIp", "None"])

    return params


@dataclass
class Params:
    pathToShooterGame: str = None
    serverPort: int = None
    targetPort: int = None
    targetIp: str = None


def extract_params():
    params = Params()
    if os.path.exists("params.csv"):
        with open("params.csv", encoding="utf8", newline="") as f:
            data = csv.reader(f)
            for line in data:
                if line[1] != "None":
                    setattr(params, line[0], line[1])
    else:
        with open("params.csv", encoding="utf8", newline="") as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows([["pathToShooterGame", "None"], ["serverPort", "None"], ["targetPort", "None"],
                              ["targetIp", "None"]])

    return params


def update_param(param, value):
    params = extract_params()
    setattr(params, param, value)
    with open("params.csv", "w", encoding="utf8", newline="") as f:
        writer = csv.writer(f, delimiter=',')
        for key, value in params.__dict__.items():
            if value is None:
                value = "None"
            writer.writerow([key, value])


update_param("targetIp", "192.168.1.1")
