from typing_extensions import TypedDict


class StudyExists(TypedDict, total=False):
    input: bool
    output: bool
    studydir: bool
    mysql: bool
    mongo: bool
    obs: bool
