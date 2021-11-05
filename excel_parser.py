from unicodedata import normalize as norm
import re
import pandas as pd


class LINE_ID:
    SHEET = 1
    LINE = 2


def normalize(data: dict):
    res = {}
    for item in data.items():
        res[item[0]] = norm("NFKC", str(item[1])).strip()
    return res


class ExcelParser:

    def __init__(self, filepath, schema, strict=False, last_line=None):
        try:
            self.xl = pd.ExcelFile(filepath)
            self.sheets = self.xl.sheet_names
        except Exception as e:
            raise AttributeError("Couldn't find such file: " + filepath)
        self.schema = schema
        self.strict = strict
        self.last_line = last_line

    def get_next_line(self):
        if self.last_line is None:
            self.last_line = {LINE_ID.SHEET: 0, LINE_ID.LINE: 0}  # Default behaviour, if no save available

        while self.last_line[LINE_ID.SHEET] < len(self.sheets):
            df = self.xl.parse(self.sheets[self.last_line[LINE_ID.SHEET]])
            rows = [i[1] for i in df.iterrows()][self.last_line[LINE_ID.LINE]::]  # repacking dataframe in a matrix
            for line in rows:
                result = {key: data for key, data in zip(self.schema, line)}  # repacking results
                self.last_line[LINE_ID.LINE] += 1  # iterating over lines, in case of save
                n_result = normalize(result)
                yield n_result
            self.last_line = {LINE_ID.SHEET: self.last_line[LINE_ID.SHEET] + 1,
                              LINE_ID.LINE: 0}  # iterating over sheets
