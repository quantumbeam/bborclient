from pydantic import BaseModel, Field, computed_field, ConfigDict
from typing import TypeAlias, Annotated, DefaultDict
from collections import defaultdict
from enum import Enum


class QueueScope(BaseModel):
    highest: int = 0
    high: int = 0
    mid: int = 0
    low: int = 0

    @computed_field
    @property
    def total(self) -> int:
        return sum((
            self.highest,
            self.high,
            self.mid,
            self.low,
        ))


class AssignedMixin(BaseModel):
    assigned: int = 0
    '''Number of tasks assigned to workers'''

    processing: int = 0
    '''Number of tasks being processed'''

class FinishedMixin(BaseModel):
    success: int = 0
    '''Number of tasks completed successfully'''

    failure: int = 0
    ''' Number of tasks failed'''

    others: int = 0
    '''Number of tasks in other states'''

class StudyIdMixin(BaseModel):
    id: str

class UserScope(
    AssignedMixin,
    FinishedMixin,
):
    @computed_field
    @property
    def total(self) -> int:
        '''Number of tasks in all states'''
        return sum((
            # self.queued.total,
            self.assigned,
            self.processing,
            self.success,
            self.failure,
            self.others,
        ))

class StudyScope(
    UserScope,
    StudyIdMixin
):...


class WorkerStatus(Enum):
    ON = 'on'
    OFF = 'off'
    UNKNOWN = 'unknown'


WorkerName: TypeAlias = str

class WorkerScope(
    AssignedMixin,
    FinishedMixin,
):
    # name: str
    description: str|None = None
    state: WorkerStatus = WorkerStatus.UNKNOWN
    # processes: int|None = None

    model_config = ConfigDict(
        use_enum_values=True,
    )


class TaskAggregation(BaseModel):
    user: UserScope = Field(default_factory=UserScope)
    '''Number of tasks belonging to a user in each task state'''

    study: StudyScope|None = None
    '''Number of tasks of a specified study in each task state'''

    queues: QueueScope = Field(default_factory=QueueScope)

    workers: DefaultDict[
        WorkerName,
        Annotated[WorkerScope, Field(default_factory=WorkerScope)]
    ] = Field(default_factory=lambda: defaultdict(WorkerScope))



