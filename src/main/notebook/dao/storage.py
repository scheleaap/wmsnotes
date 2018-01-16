# -*- coding: utf-8 -*-
import io

from notebook.aggregate import Note
from notebook.dao import NoteRepository
from notebook.storage import NotebookStorage


class StorageNoteRepository(NoteRepository):
    """TODO
    """

    def __init__(self, storage: NotebookStorage):
        self.storage = storage

    def add_or_update_note(self, note: Note):
        self.storage.set_note_payload(note.note_id, 'main', io.BytesIO(bytes(note.payload, encoding='utf-8')))

    def get_all_notes(self):
        for note in self.storage.get_all_notes():
            yield note

    def get_note(self, note_id) -> Note:
        note = self.storage.get_note(note_id)
        payload_file = self.storage.get_note_payload(note_id, 'main')
        try:
            # TODO
            note._payload = str(payload_file.read(), encoding='utf-8')
        finally:
            payload_file.close()
        return note

    def has_note(self, note_id) -> bool:
        return self.storage.has_note(note_id)
