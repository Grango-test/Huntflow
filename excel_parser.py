import os.path
from unicodedata import normalize as norm
import re
import pandas as pd
import pickle

class LINE_ID:
    SHEET = 1
    LINE = 2


def normalize(data: dict):
    res = {}
    for item in data.items():
        res[item[0]] = norm("NFKC", str(item[1])).strip()
    return res


class ExcelParser:

    def __init__(self, filepath, schema, strict=False):
        try:
            self.xl = pd.ExcelFile(filepath)
            self.sheets = self.xl.sheet_names
        except Exception as e:
            raise AttributeError("Couldn't find such file: " + filepath)
        self.schema = schema
        self.strict = strict
        self.savepath = os.path.join(os.path.dirname(filepath), "save")
        if os.path.isfile(self.savepath):
            savefile = open(self.savepath, "rb")
            self.last_line = pickle.load(savefile)
            savefile.close()
        else:
            self.last_line = None

    def get_next_line(self):
        try:
            if self.last_line is None:
                self.last_line = {LINE_ID.SHEET: 0, LINE_ID.LINE: 0}  # Default behaviour, if no save available

            while self.last_line[LINE_ID.SHEET] < len(self.sheets):
                df = self.xl.parse(self.sheets[self.last_line[LINE_ID.SHEET]])
                rows = [i[1] for i in df.iterrows()][self.last_line[LINE_ID.LINE]::]  # repacking dataframe in a matrix
                for line in rows:
                    result = {key: data for key, data in zip(self.schema, line)}  # repacking results
                    n_result = normalize(result)
                    yield n_result
                    self.last_line[LINE_ID.LINE] += 1  # iterating over lines, in case of save
                self.last_line = {LINE_ID.SHEET: self.last_line[LINE_ID.SHEET] + 1,
                                  LINE_ID.LINE: 0}  # iterating over sheets
        finally:
            if os.path.isfile(self.savepath):
                os.remove(self.savepath)

    def save(self):
        savefile = open(self.savepath, "wb")
        pickle.dump(self.last_line, savefile)
        savefile.close()

