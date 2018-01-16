# -*- coding: utf-8 -*-
from notebook.aggregate import Note
from notebook.dao import NoteRepository
from notebook.storage import NoteDoesNotExistError


class InMemoryNoteRepository(NoteRepository):
    """Stores notes in memory.
    """

    def __init__(self):
        self.notes = dict()

    def add_or_update_note(self, note: Note):
        self.notes[note.note_id] = note

    def get_all_notes(self):
        for note in self.notes.values():
            yield note

    def get_note(self, note_id) -> Note:
        if not self.has_note(note_id):
            raise NoteDoesNotExistError
        return self.notes[note_id]

    def has_note(self, note_id) -> bool:
        return note_id in self.notes
