from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from parsers import PersonDetailView


def render_patient_as_list(patients: List[PersonDetailView]) -> str:
    result = ''
    for item, patient in enumerate(patients):
        result += f'{item + 1}: {patient.fio} \n'
    return result


def render_patient_as_inline_buttons(patients: List[PersonDetailView]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for patient in patients:
        keyboard.add(InlineKeyboardButton(text=patient.fio, callback_data=f'patient_info_{patient.person_id}'))
    return keyboard


def render_patient_detail_view(patient: PersonDetailView) -> str:
    response = ''
    response += f'{patient.fio} \n \n'
    sorted_set = sorted(patient.events, key=lambda x: x.date, reverse=True)
    for item, event in enumerate(sorted_set):
        response += f'{event.date} {event.header} {event.status} \n'
        response += f'{event.body} \n \n'
    return response


__all__ = ['render_patient_as_list', 'render_patient_as_inline_buttons', 'render_patient_detail_view']
