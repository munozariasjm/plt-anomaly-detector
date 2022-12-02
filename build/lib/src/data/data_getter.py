import glob
import pandas as pd
import tables
import numpy as np
import numba as nb
import datetime
import dateutil
import math


@nb.njit
def get_mu(timestamp_data):
    numorbits = math.ceil(float(max(timestamp_data)) / 1024.0) * 1024.0
    return -np.log(timestamp_data / numorbits)


class LocalFileExplorer:
    def __init__(self, mount_path: str):
        self.mount_path = mount_path
        if not self.mount_path.endswith("/"):
            self.mount_path += "/"

    def get_available_files(self, fill_number):
        return glob.glob(f"{self.mount_path}{fill_number}/*")

    @staticmethod
    @nb.njit
    def fast_data_agg(timestamp_data):
        integrals = []
        for i in nb.prange(0, len(timestamp_data)):
            datalist = timestamp_data[i][0]
            mu = get_mu(datalist)
            integral = np.mean(mu)
            integrals.append(integral)
        return integrals

    def _get_raw_dataframe(self, file_path):
        with tables.open_file(file_path) as f:
            ins = self.fast_data_agg(f.root.pltaggzero[:][["data"]])
            df = pd.DataFrame(
                f.root.pltaggzero[:][
                    [col for col in f.root.pltaggzero.colnames if col != "data"]
                ]
            )
            df["data"] = ins
        return df

    def _transform_df(self, df):
        return df

    @staticmethod
    @nb.njit
    def to_dt(seconds: np.array, miliseconds: np.array):
        """Converts the miliseconds array to a range
        considering if a new second was inserted
        """
        dt = np.zeros(len(seconds))
        dt[0] = miliseconds[0]
        for i in nb.prange(1, len(seconds)):
            if seconds[i] != seconds[i - 1]:
                dt[i] = miliseconds[i]
            else:
                dt[i] = dt[i - 1] + miliseconds[i]
        return dt

    def correct_time_idnex(self, df, start_date):
        date = start_date
        seconds = df.apply(
            lambda x: float(f"{x['timestampsec']}"),
            axis=1,
        )
        dt = pd.to_datetime(pd.Series(seconds), unit="s")
        dt = date + (dt - dt.min())
        return dt

    def extract_data_from_name(self, file_name, df):
        fill_name = file_name.split("/")[-1]
        fill_number = fill_name.split("_")[1]
        start_date = datetime.datetime.strptime(
            "20" + fill_name.split("_")[-2], "%Y%m%d%H%M%S"
        )
        if len(df) > 0:
            dt = self.correct_time_idnex(df, start_date)
        else:
            dt = pd.Series([])
        return fill_number, start_date, dt

    def get_complete_dataframe(self, fill_number):
        fill_files = self.get_available_files(fill_number)
        dfs = []
        for i, file_path in enumerate(fill_files):
            try:
                fdf = self._get_raw_dataframe(file_path)
                fill_number, start_date, dt = self.extract_data_from_name(
                    file_path, fdf
                )
                fdf["dt"] = dt
                dfs.append(fdf)
            except Exception as e:
                print(e)
                print(f"{file_path} does not contain pltaggzero data")

        dfs = pd.concat(dfs)
        return dfs.reset_index(drop=False)

    def get_single_dataframe(self, fill_number, i):
        fill_files = self.get_available_files(fill_number)
        file_path = fill_files[i]
        try:
            fdf = self._get_raw_dataframe(file_path)
            fill_number, start_date, dt = self.extract_data_from_name(file_path, fdf)
            fdf["dt"] = dt
        except Exception as e:
            print(e)
            print(f"{file_path} does not contain dessired data")
            return

        return fdf.reset_index(drop=False)


class DataParser:
    def __init__(self, mount_path):
        self.mount_path = mount_path
        self.data_getter = LocalFileExplorer(mount_path)

    def get_raw_data(self, fill_number: str, subsample: int = 1) -> pd.DataFrame:
        """Returns the raw data for a given fill number

        Args:
            fill_number (int | str): Fill number to be searched
            subsample (int, optional): Sample the integrated data to
            speed-up anomaly searches. Defaults to 1.

        Returns:
            pd.DataFrame: The pivoted data per channel to generate
                for each one of the fills, the index is the timestamp.
        """
        available_fills = self.data_getter.get_available_files(fill_number)
        print(f"Found {len(available_fills)} runs for fill {fill_number}")
        dfs = []
        for i in range(len(available_fills)):
            try:
                df = self.data_getter.get_single_dataframe(fill_number, i)
                df = df.pivot_table(
                    index=["dt"], columns="channelid", values="data"
                ).dropna()
                dfs.append(df)
            except Exception as e:
                print(f"Problem with fill {fill_number}, {i}")
                print(e)
        if not subsample:
            subsample = 1
        complete_df = pd.concat(dfs).sort_index()
        sample_df = complete_df.iloc[::subsample]
        int_df = self._resample_and_interpolate(sample_df).sort_index()
        return int_df

    def _resample_and_interpolate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Resamples the dataframe and interpolates the missing values

        Args:
            data (pd.DataFrame): Dataframe with the data

        Returns:
            pd.DataFrame: Resampled dataframe
        """
        return data.resample("1S").mean().interpolate(method="linear")
