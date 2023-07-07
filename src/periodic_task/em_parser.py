import asyncio
from typing import List, Set

from database import DataBase, PatientEvents
from parsers import EventDetailView, Parser, PersonDetailView
from settings import ApiWrapper


async def get_person_detail_from_api(patients_id_list: List[int]) -> Set[PersonDetailView]:
    tasks = []
    async with ApiWrapper() as api:
        for patient in patients_id_list:
            tasks.append(api.person_detail_view(patient))
        responses = await asyncio.gather(*tasks)
    parse_data = {Parser(response).parse_person_detail() for response in responses}
    return parse_data


async def get_patients_id_list() -> List[int]:
    async with ApiWrapper() as api:
        response = await api.get_patient_information()
    wards, patients_id_list = Parser(response).parse_ward_and_patient()
    return patients_id_list


async def get_patients_info_from_sites() -> Set[PersonDetailView]:
    patients_id_list = await get_patients_id_list()
    parse_data: Set[PersonDetailView] = await get_person_detail_from_api(patients_id_list)
    return parse_data


async def get_patients_info_from_db() -> Set[PersonDetailView]:
    async with DataBase() as db:
        patients = await db.get_patients()
    result = {patient.to_tuple() for patient in patients}
    return result


def _events_db_to_named_tuple(
    patients_event_list: List[List[PatientEvents]],
) -> List[Set[EventDetailView]]:
    result = []
    for events in patients_event_list:
        events_set = {event.to_tuple() for event in events}
        result.append(events_set)
    return result


async def get_change_events_persons(patients: Set[PersonDetailView]):
    async with DataBase() as db:
        tasks = [db.get_patient_events(patient) for patient in patients]
        patients_events_list = await asyncio.gather(*tasks)
        patient_events_set = _events_db_to_named_tuple(patients_events_list)
        for events_from_db, patient in zip(patient_events_set, patients):
            received_events = patient.events.difference(events_from_db)
            delete_events = events_from_db.difference(patient.events)
            await db.delete_events_set(delete_events)
            await db.add_patient_events(patient, received_events)


async def add_received_patients(patients: Set[PersonDetailView]):
    async with DataBase() as db:
        await db.add_patient_set(patients)


async def delete_patients(patients: Set[PersonDetailView]):
    async with DataBase() as db:
        await db.delete_patients_set(patients)


async def em_parser() -> Set[PersonDetailView]:
    patients_from_site: Set[PersonDetailView] = await get_patients_info_from_sites()
    patients_from_db: Set[PersonDetailView] = await get_patients_info_from_db()
    received_patients = patients_from_site.difference(patients_from_db)
    delete_patients_set = patients_from_db.difference(patients_from_site)
    unchanged_patients = patients_from_site - received_patients
    await add_received_patients(received_patients)
    await get_change_events_persons(unchanged_patients)
    await delete_patients(delete_patients_set)
    return received_patients


__all__ = [
    'em_parser',
]
