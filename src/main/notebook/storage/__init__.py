# -*- coding: utf-8 -*-
# TODO: Rename to "Note"
from notebook.aggregate import Note

__all__ = [
    'NotebookStorage',
    'NoteDoesNotExistError',
]


class NotebookStorage:
    """Classes implementing this interface can store notebooks.
    """

    def get_all_notes(self):
        """Loads the metadata of all notes in the notebook.

        @return: An iterable returning Note objects.
        @raise IOError: If one or notes cannot be read.
        @raise ParseError: If the file has an invalid syntax.
        """
        raise NotImplementedError(self.get_all_notes.__name__)

    def get_note(self, note_id) -> Note:
        """Loads the metadata of a note in the notebook.

        @param note_id: The id of the note to be read.
        @return: A Note.
        @raise NoteDoesNotExistError: If a note with the id does not exist.
        @raise IOError: If the note cannot be read.
        @raise ParseError: If the file has an invalid syntax.
        """
        raise NotImplementedError(self.get_note.__name__)

    def get_note_payload(self, note_id, payload_name):
        """Loads a payload of a note in the notebook.

        @param note_id: The id of the note.
        @param payload_name: The name of the payload.
        @return: A file-like object with the payload data.
        @raise NoteDoesNotExistError: If a note with the id does not exist.
        @raise PayloadDoesNotExistError: If a payload with the name does not exist.
        @raise IOError: If the payload cannot be read.
        """
        raise NotImplementedError(self.get_note_payload.__name__)

    def has_note(self, note_id):
        """Returns whether a note exists within the notebook.

        @param note_id: The id of the note.
        @return Whether a note exists within the notebook.
        """
        raise NotImplementedError(self.has_note.__name__)

    def set_note_payload(self, note_id, payload_name, payload_file):
        """Sets a payload for a note.

        @param note_id: The id of the note.
        @param payload_name: The name of the new payload. Must be unique for the note.
        @param payload_file: A file-like object with the payload data.
        @raise NoteDoesNotExistError: If a note with the id does not exist.
        """
        raise NotImplementedError(self.set_note_payload.__name__)


class NoteDoesNotExistError(Exception):
    pass


class ParseError(Exception):
    pass


class PayloadDoesNotExistError(Exception):
    pass
