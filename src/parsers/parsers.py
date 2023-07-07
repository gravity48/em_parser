import json
from datetime import datetime
from typing import Dict, List, NamedTuple, Set


class WardsPatientViews(NamedTuple):
    wards: List
    patients: List[int]


class EventDetailView(NamedTuple):
    event_id: str
    header: str
    status: str
    body: str
    date: datetime

    def __eq__(self, other):
        if isinstance(other, EventDetailView):
            return other.event_id == self.event_id
        return False


class PersonDetailView(NamedTuple):
    person_id: str
    fio: str
    birthday: datetime
    events: Set[EventDetailView]

    def __eq__(self, other):
        if isinstance(other, PersonDetailView):
            return self.person_id == other.person_id
        return False

    def __hash__(self):
        return hash((self.person_id, self.fio, self.birthday))


class Parser:
    def __init__(self, data: str):
        self._data = data

    def parse_ward_and_patient(self):
        data: List[Dict] = json.loads(self._data)
        wards = []
        patients: List[int] = []
        for item in data:
            if item.get('Person_id', False):
                patients.append(int(item['Person_id']))
            else:
                wards.append(item)
        return WardsPatientViews(wards, patients)

    @staticmethod
    def _parse_event_list(data: list, events: set):
        for event in data:
            event_id = event['Evn_id']
            header = event['Evn_Header']
            status = event['EvnStatus_Name']
            body = event['Evn_Body']
            date = datetime.strptime(event['Evn_DT'], '%d.%m.%Y %H:%M')
            events.add(EventDetailView(event_id, header, status, body, date))

    @staticmethod
    def _parse_event_dict(data: dict, events: set):
        for event in data.values():
            event_id = event['Evn_id']
            header = event['Evn_Header']
            status = event['EvnStatus_Name']
            body = event['Evn_Body']
            date = datetime.strptime(event['Evn_DT'], '%d.%m.%Y %H:%M')
            events.add(EventDetailView(event_id, header, status, body, date))

    def parse_person_detail(self):
        data: Dict = json.loads(self._data)
        events: Set[EventDetailView] = set()
        if isinstance(data['data']['evn'], list):
            self._parse_event_list(data['data']['evn'], events)
        elif isinstance(data['data']['evn'], dict):
            self._parse_event_dict(data['data']['evn'], events)
        person_id = data['data']['Person_id']
        person_fio = data['data']['Person_Fio']
        person_birthday = datetime.strptime(data['data']['Person_BirthDay'], '%d.%m.%Y')
        person = PersonDetailView(person_id, person_fio, person_birthday, events)
        return person
