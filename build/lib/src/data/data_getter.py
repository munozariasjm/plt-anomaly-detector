import glob
import pandas as pd
import tables
import numpy as np
import numba as nb
import datetime


class LocalFileExplorer:
    """Tool to explore the hdf5 files on a mount_path."""
    def __init__(self,
                 mount_path: str) -> None:
        """Initialize the class with the path to
        the mount point of the data."""
        self.mount_path = mount_path

    def get_available_files(self,
                            fill_number: int) -> list:
        """Lists all the files in the
        mount_path that contain the fill_number."""
        return glob.glob(f"{self.mount_path}/{fill_number}/*")

    @staticmethod
    @nb.njit
    def fast_data_agg(timestamp_data: pd.DataFrame) -> pd.Series:
        """Agregation tool to agregate the data in the timestamp_data.
            The agregation is done via a nopython jit function of Numba.
        """
        integrals = []
        for i in nb.prange(0, len(timestamp_data)):
            datalist = timestamp_data[i][0]
            integral = np.sum(datalist)
            integrals.append(integral)
        return integrals

    def _get_raw_dataframe(self,
                           file_path: str) -> pd.DataFrame:
        """Returns a dataframe with the raw data from the file_path,
        readed from the hdf5 file via pytables.

        Args:
            file_path (str): The path to the hdf5 file.

        Returns:
            DataFrame: Dataframe with the raw data from the file_path.
        """
        with tables.open_file(file_path) as f:
            ins = self.fast_data_agg(f.root.pltaggzero[:][["data"]])
            df = pd.DataFrame(
                f.root.pltaggzero[:][
                    [c for c in f.root.pltaggzero.colnames if c != "data"]
                ]
            )
            df["data"] = ins
        return df

    def _transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Utility function to transform the dataframe to the format.
        For now, left as a placeholder.

        Args:
            df (pd.DataFrame): Raw dataframe from the hdf5 file.

        Returns:
            pd.DataFrame: Readed dataframe
        """
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

    def get_complete_dataframe(self, fill_number, verbose=False):
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
                if verbose:
                    print(e)
                print(f"{file_path} does not contain pltaggzero data")

        dfs = pd.concat(dfs)
        return dfs.reset_index(drop=False)

    def get_single_dataframe(self, fill_number, i, verbose=False):
        fill_files = self.get_available_files(fill_number)
        file_path = fill_files[i]
        try:
            fdf = self._get_raw_dataframe(file_path)
            f_num, start_date, dt = self.extract_data_from_name(file_path,
                                                                fdf)
            fdf["dt"] = dt
        except Exception as e:
            if verbose:
                print(e)
                print(f"{file_path} does not contain pltaggzero data")
            return

        return fdf.reset_index(drop=False)
