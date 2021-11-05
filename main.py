# coding: utf8
import sys
from unicodedata import normalize

import api_driver
import excel_parser
import os


TOKEN_ARG = ['token', 't', '-t', '-token']
PATH_ARG = ['path', 'p', '-p', '-path']


def get_arg(names, args):
    for name in names:
        result = args.get(name)
        if result is not None:
            return result
    raise AttributeError()


def find_file(position, name, path):
    root_dir = os.path.dirname(path)
    dir = os.path.join(root_dir, position)
    if position in os.listdir(root_dir):
        files = [i for i in os.walk(dir)][0][2]
        for file in files:
            if normalize("NFKC", file).startswith(name):
                return os.path.join(dir, file)


if __name__ == "__main__":
    arguments = {i.split("=")[0]: i.split("=")[1] for i in sys.argv[1::]}
    token = get_arg(TOKEN_ARG, arguments)
    path = get_arg(PATH_ARG, arguments)

    xlparser = excel_parser.ExcelParser(path, ["position", "full_name", "wage", "comment", "status"])
    driver = api_driver.ApiDriver(token, "https://dev-100-api.huntflow.dev/")
    for i in xlparser.get_next_line():
        file = find_file(i["position"], i["full_name"], path)
        file_parsed = driver.add_file(file)
        applicant_id = driver.add_applicant(i, file_parsed)
        driver.match_vacancy_and_candidate(applicant_id, i["position"], i["status"], i["comment"], file_parsed["file_id"])


