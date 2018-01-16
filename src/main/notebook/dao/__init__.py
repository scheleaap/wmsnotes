# -*- coding: utf-8 -*-
from notebook.aggregate import Note


class NoteRepository(object):
    """Classes implementing this interface can store notebooks.
    """

    def add_or_update_note(self, note):
        """TODO
        """
        raise NotImplementedError(self.has_note.__name__)

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

    def has_note(self, note_id) -> bool:
        """Returns whether a note exists within the notebook.

        @param note_id: The id of the note.
        @return Whether a note exists within the notebook.
        """
        raise NotImplementedError(self.has_note.__name__)
