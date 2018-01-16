# -*- coding: utf-8 -*-
from notebook.aggregate import Note
from notebook.dao import NoteRepository


class DelayedPersistNoteRepository(NoteRepository):
    """TODO
    """

    def __init__(self, repository1: NoteRepository, repository2: NoteRepository):
        self.repository1 = repository1
        self.repository2 = repository2
        self.note_ids_added_or_updated = set()
        self.note_ids_deleted = set()

    def add_or_update_note(self, note: Note):
        self.repository1.add_or_update_note(note)
        self.note_ids_added_or_updated.add(note.note_id)

    def get_all_notes(self):
        notes1_ids = set()
        for note in self.repository1.get_all_notes():
            notes1_ids.add(note.note_id)
            yield note
        for note in self.repository2.get_all_notes():
            if note.note_id not in notes1_ids:
                yield note

    def get_note(self, note_id) -> Note:
        if self.repository1.has_note(note_id):
            return self.repository1.get_note(note_id)
        else:
            return self.repository2.get_note(note_id)

    def has_note(self, note_id) -> bool:
        return self.repository1.has_note(note_id) or \
               self.repository2.has_note(note_id)

    def persist(self):
        for note in self.repository1.get_all_notes():
            self.repository2.add_or_update_note(note)
