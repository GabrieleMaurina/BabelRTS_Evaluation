import pandas


class Folders:
    def __init__(self, file, default_src, default_test):
        self.file = file
        self.default_src = default_src
        self.default_test = default_test
        self.data = pandas.read_csv(file, dtype=str, na_filter=False)
        for col in self.data.columns:
            self.data[col] = self.data[col].str.strip()

    def get_folders(self, sut, version):
        rows = self.data[self.data['sut'] == sut]
        for row in rows.itertuples():
            if not row.version:
                return row.src, row.test
            if ':' in row.version:
                values = row.version.split(':')
                start = int(values[0]) if values[0] else None
                end = int(values[1]) if values[1] else None
                if start is None and end is None:
                    return row.src, row.test
                elif start is None:
                    if version <= end:
                        return row.src, row.test
                elif end is None:
                    if version >= start:
                        return row.src, row.test
                else:
                    if start <= version <= end:
                        return row.src, row.test
            else:
                value = int(row.version)
                if value == version:
                    return row.src, row.test
        return self.default_src, self.default_test
