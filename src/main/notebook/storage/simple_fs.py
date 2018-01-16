# -*- coding: utf-8 -*-
"""File system storage."""

from __future__ import absolute_import

import hashlib
import io
import logging
import os

from . import *
from ..aggregate import Note, FolderPath

__all__ = ['SimpleFileSystemStorage']


class SimpleFileSystemStorage(NotebookStorage):
    def __init__(self, dir):
        """Constructor.

        @param dir: The path to the directory to store notes in.
        """
        self.log = logging.getLogger('{m}.{c}'.format(m=self.__class__.__module__, c=self.__class__.__name__))
        self.dir = dir

        self.log.debug(u'dir={0}'.format(self.dir))
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

    def get_all_notes(self):
        self.log.debug(u'Loading all notes')

        def handle_error(e):
            raise e

        for (dirpath, dirnames, filenames) in os.walk(self.dir, onerror=handle_error):
            dirpath = os.path.relpath(dirpath, self.dir)
            for filename in filenames:  # type: str
                if filename.endswith('.md'):
                    note_id = os.path.normpath(os.path.join(dirpath, filename))
                    self.log.debug(u'Found a note with id "{note_id}" in {path}'.format(note_id=note_id, path=dirpath))
                    yield self.get_note(note_id)

    def get_note(self, note_id):
        self.log.debug(u'Loading note {note_id}'.format(note_id=note_id))
        if not self.has_note(note_id):
            raise NoteDoesNotExistError()

        return self._read_note(note_id)

    def _get_note_directory_path(self, note_id):
        # return os.path.join(self.dir, note_id)
        return os.path.join(self.dir, os.path.dirname(note_id))

    def _get_note_file_path(self, note_id):
        return os.path.normpath(os.path.join(self.dir, note_id))

    # def _get_notebook_file_path(self):
    #     return os.path.join(self.dir, 'notebook.xml')

    def get_note_payload(self, note_id, payload_name):
        self.log.debug(u'Loading payload "{name}" of note {note_id}'.format(note_id=note_id, name=payload_name))
        if not self.has_note(note_id):
            raise NoteDoesNotExistError(note_id)
        # if not self.has_note_payload(note_id, payload_name):
        #     raise PayloadDoesNotExistError(note_id, payload_name)

        return io.open(self._get_note_payload_file_path(note_id, payload_name), mode='rb')

    def _get_note_payload_directory_path(self, note_id):
        # return os.path.join(self.dir, note_id, 'payload')
        return self._get_note_directory_path(note_id)

    def _get_note_payload_file_path(self, note_id, payload_name):
        # return os.path.join(self.dir, note_id, 'payload', payload_name)
        return self._get_note_file_path(note_id)

    def has_note(self, note_id):
        return os.path.exists(self._get_note_file_path(note_id))

    # def has_note_payload(self, note_id, payload_name):
    #     return os.path.exists(self._get_note_payload_file_path(note_id, payload_name))

    def _read_note(self, note_id):
        """Reads a note.

        @param note_id: The id of the note.
        @return: A Note.
        """
        path = os.path.dirname(note_id)
        title = os.path.basename(note_id)[:-3]
        return Note(
            note_id=note_id,
            title=title,
            folder_path=FolderPath.from_string(path))

    def set_note_payload(self, note_id, payload_name, payload_file):
        self.log.debug(u'Storing payload "{name}" to note {note_id}'.format(note_id=note_id, name=payload_name))
        if not self.has_note(note_id):
            raise NoteDoesNotExistError(note_id)

        directory_path = self._get_note_payload_directory_path(note_id)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        with io.open(self._get_note_payload_file_path(note_id, payload_name), mode='wb') as f:
            data = payload_file.read()
            f.write(data)
            payload_hash = hashlib.md5(data).hexdigest()

        # stored_note = self.get_note(note_id)
        # stored_note.payloads.append(StoredNotePayload(payload_name, payload_hash))
        # self._write_note(note_id, stored_note)

    def __repr__(self):
        return '{cls}[{dir}]'.format(cls=self.__class__.__name__, **self.__dict__)
