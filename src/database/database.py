from typing import List, Set

from sqlalchemy import delete, update
from sqlalchemy.engine import ScalarResult
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import Select

from parsers import EventDetailView, PersonDetailView

from .tables import PatientEvents, Patients, Settings, Tasks, Users


class SqliteDB:
    def __init__(self):
        self.connection_string = 'sqlite+aiosqlite:///database.sqlite3'

    def __await__(self):
        return self.session

    async def __aenter__(self):
        self.engine = create_async_engine(self.connection_string)
        self.async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
        self.session = self.async_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        await self.engine.dispose()

    @staticmethod
    def _gen_patient_obj(patient: PersonDetailView) -> Patients:
        events = []
        for event in patient.events:
            events.append(
                PatientEvents(
                    event_id=event.event_id,
                    header=event.header,
                    status=event.status,
                    body=event.body,
                    date=event.date,
                ),
            )
        patient = Patients(person_id=patient.person_id, fio=patient.fio, birthday=patient.birthday)
        patient.events = events
        return patient

    async def update_page_id_user(self, page_id: int, user_id: int):
        query = update(Users).where(Users.id == user_id).values(page_id=page_id)
        await self.session.execute(query)
        await self.session.commit()

    async def get_or_create_user(
        self,
        user_id: int,
        username: str,
        first_name: str,
        last_name: str,
        chat_id: int,
    ):
        try:
            query: Select = select(Users).where(Users.user_id == user_id)
            result: ScalarResult = await self.session.scalars(query)
            return result.one()
        except NoResultFound:
            user: Users = Users(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                chat_id=chat_id,
            )
            self.session.add(user)
            await self.session.commit()
            return user

    async def get_staff_users(self) -> List[Users]:
        query = select(Users).where(Users.is_staff == True)
        result = await self.session.scalars(query)
        return result.all()

    async def get_patient(self, patient: PersonDetailView) -> Patients:
        query: Select = select(Patients).where(Patients.person_id == patient.person_id)
        result: ScalarResult = await self.session.scalars(query)
        return result.one()

    async def get_patient_by_person_id(self, person_id: str) -> Patients:
        query: Select = select(Patients).where(Patients.person_id == person_id)
        result: ScalarResult = await self.session.scalars(query)
        return result.one()

    async def get_patients(self) -> List[Patients]:
        query = select(Patients).order_by(Patients.receipt_date.desc())
        result: ScalarResult = await self.session.scalars(query)
        return result.all()

    async def get_patient_events(self, patient: PersonDetailView) -> List[PatientEvents]:
        patient_db = await self.get_patient(patient)
        query: Select = (
            select(PatientEvents)
            .where(PatientEvents.patient_id == patient_db.id)
            .order_by(PatientEvents.date)
        )
        result: ScalarResult = await self.session.scalars(query)
        events: List[PatientEvents] = result.all()
        return events

    async def get_patient_events_by_patient_id(self, patient_id: int) -> List[PatientEvents]:
        query: Select = (
            select(PatientEvents)
            .where(PatientEvents.patient_id == patient_id)
            .order_by(PatientEvents.date)
        )
        result: ScalarResult = await self.session.scalars(query)
        events: List[PatientEvents] = result.all()
        return events

    async def delete_user(self, user_id: int):
        query = delete(Users).where(Users.id == user_id)
        await self.session.execute(query)
        await self.session.commit()

    async def delete_events_set(self, events: Set[EventDetailView]):
        event_id_list = [event.event_id for event in events]
        query = delete(PatientEvents).where(PatientEvents.event_id.in_(event_id_list))
        await self.session.execute(query)
        await self.session.commit()

    async def delete_patients_set(self, patients: Set[PersonDetailView]):
        person_id_list = [patient.person_id for patient in patients]
        query = delete(Patients).where(Patients.person_id.in_(person_id_list))
        await self.session.execute(query)
        await self.session.commit()

    async def add_task(self, status: bool, status_text: str):
        task = Tasks(status=status, status_text=status_text)
        self.session.add(task)
        await self.session.commit()

    async def add_patient(self, patient: PersonDetailView):
        patient_obj = self._gen_patient_obj(patient)
        self.session.add(patient_obj)
        await self.session.commit()

    async def add_patient_set(self, patients: Set[PersonDetailView]):
        for patient in patients:
            self.session.add(self._gen_patient_obj(patient))
        await self.session.commit()

    async def add_patient_events(self, patient: PersonDetailView, events: Set[EventDetailView]):
        patient_db = await self.get_patient(patient)
        for event in events:
            self.session.add(
                PatientEvents(
                    person_id=patient_db.id,
                    event_id=event.event_id,
                    header=event.header,
                    status=event.status,
                    body=event.body,
                    date=event.date,
                ),
            )

        await self.session.commit()

    async def get_cookies(self) -> str:
        query: Select = select(Settings).where(Settings.name == 'phpsessid')
        result: ScalarResult = await self.session.scalars(query)
        cookies: Settings = result.one()
        return cookies.value

    async def update_cookies(self, value: str):
        query = update(Settings).where(Settings.name == 'phpsessid').values(value=value)
        await self.session.execute(query)
        await self.session.commit()


class DataBase:
    instance: SqliteDB = None

    def __new__(cls, *args, **kwargs):
        return SqliteDB()

    @classmethod
    def init_sqlite_db(cls, *args, **kwargs):
        cls.instance = SqliteDB()


__all__ = ['DataBase', 'PatientEvents']
