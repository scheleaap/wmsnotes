# -*- coding: utf-8 -*-

import os

__all__ = [
    'Note',
]


class NoteCreated(object):
    def __init__(self, note):
        self.note = note  # type: Note

    def __repr__(self):
        return '{cls}[{note}]'.format(cls=self.__class__.__name__, **self.__dict__)


class NotePayloadChanged(object):
    def __init__(self, note_id: str, new_payload: str):
        self.note_id = note_id
        self.new_payload = new_payload

    def __repr__(self):
        return '{cls}[{note_id}, new payload length={len}]'.format(
            cls=self.__class__.__name__,
            len=len(self.new_payload),
            **self.__dict__)


class FolderPath(object):
    @staticmethod
    def from_string(string_path: str):
        if string_path is None:
            return FolderPath([])
        else:
            stripped_string_path = string_path.strip()
            if stripped_string_path == '':
                return FolderPath([])
            else:
                return FolderPath(stripped_string_path.split(os.sep))

    def __init__(self, elements):
        self.elements = elements

    def __eq__(self, other):
        return \
            isinstance(other, self.__class__) and \
            self.elements == other.elements

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '{cls}[{path}]'.format(
            cls=self.__class__.__name__,
            path='/'.join(self.elements),
            **self.__dict__
        )


class Note(object):
    """A note in a notebook.

    @ivar note_id: The id of the note.
    @ivar title: The title of the note.
    @ivar folder_path: The path of the note's folder.
    @ivar payload: The payload of the note.
    """

    def __init__(
            self,
            note_id: str,
            title: str,
            folder_path: FolderPath,
            payload: str = None,
    ):
        """Constructor.

        @param note_id: See the class documentation.
        @param title: See the class documentation.
        @param folder_path: See the class documentation.
        @param payload: See the class documentation.
        """
        self._title = title
        self._note_id = note_id
        self._folder_path = folder_path
        self._payload = payload

    def create(self) -> NoteCreated:
        return NoteCreated(self)

    @property
    def note_id(self):
        return self._note_id

    @property
    def folder_path(self):
        return self._folder_path

    # @folder_path.setter
    # def folder_path(self, folder_path):
    #     self._folder_path = folder_path

    @property
    def title(self):
        return self._title

    # @title.setter
    # def title(self, title):
    #     self._title = title

    @property
    def payload(self):
        return self._payload

    def set_payload(self, payload) -> NotePayloadChanged:
        self._payload = payload
        return NotePayloadChanged(self.note_id, payload)

    def __repr__(self):
        return '{cls}[id={_note_id}, folder={_folder_path}, title={_title}, payload={payload_length}]'.format(
            cls=self.__class__.__name__,
            payload_length=len(self.payload) if self.payload is not None else 'N/A',
            **self.__dict__
        )
