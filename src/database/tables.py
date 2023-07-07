from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

from parsers import EventDetailView, PersonDetailView

GREETING_MESSAGE_ID = 1

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True)
    username = Column(Text, nullable=True)
    first_name = Column(Text, nullable=True)
    last_name = Column(Text, nullable=True)
    chat_id = Column(BigInteger)
    page_id = Column(Integer, default=0)
    is_staff = Column(Boolean, default=False)

    def __init__(
        self,
        user_id: int,
        username: str,
        first_name: str,
        last_name: str,
        chat_id: int,
        *args,
        **kwargs,
    ):
        super(Users, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.chat_id = chat_id


class Patients(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Text)
    fio = Column(Text)
    birthday = Column(DateTime)
    receipt_date = Column(DateTime)

    events = relationship('PatientEvents', back_populates='patient')

    def to_tuple(self) -> PersonDetailView:
        return PersonDetailView(self.person_id, self.fio, self.birthday, set())

    def __init__(self, person_id: str, fio: str, birthday: datetime, *args, **kwargs):
        super(Patients, self).__init__(*args, **kwargs)
        self.person_id = person_id
        self.fio = fio
        self.birthday = birthday
        self.receipt_date = datetime.now()


class PatientEvents(Base):
    __tablename__ = 'patient_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'))
    event_id = Column(Text)
    header = Column(Text)
    status = Column(Text)
    body = Column(Text)
    date = Column(DateTime)

    patient = relationship('Patients', back_populates='events', cascade='all, delete')

    def to_tuple(self) -> EventDetailView:
        return EventDetailView(self.event_id, self.header, self.status, self.body, self.date)

    def __init__(
        self,
        event_id: str,
        header: str,
        status: str,
        body: str,
        date: datetime,
        person_id=None,
        *args,
        **kwargs,
    ):
        super(PatientEvents, self).__init__(*args, **kwargs)
        self.event_id = event_id
        self.header = header
        self.status = status
        self.body = body
        self.date = date
        self.patient_id = person_id


class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime)
    status = Column(Boolean)
    status_text = Column(Text)

    def __init__(self, status: bool, status_text: str, *args, **kwargs):
        super(Tasks, self).__init__(*args, **kwargs)
        self.date = datetime.now()
        self.status = status
        self.status_text = status_text


class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(String)
    name = Column(String)


__all__ = ['Users', 'Patients', 'PatientEvents', 'Tasks', 'Settings']
