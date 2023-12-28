from typing import IO, Optional


class FileInfo:
    initial_dataset: Optional[IO[str]] = None
    fs: Optional[IO[str]] = None
    sfs: Optional[IO[str]] = None
    pfs: Optional[IO[str]] = None

    time_info: Optional[IO[str]] = None
    ls: Optional[IO[str]] = None

    @staticmethod
    def set_initial_file_info(init_db: str, fs: str, sfs: str, pfs: str) -> None:
        FileInfo.initial_dataset = open(init_db, "r")
        FileInfo.fs = open(fs, "w")
        FileInfo.sfs = open(sfs, "w")
        FileInfo.pfs = open(pfs, "w")
