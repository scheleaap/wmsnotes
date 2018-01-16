# -*- coding: utf-8 -*-
import io
import logging
from collections import namedtuple

import cyrusbus.bus

from notebook.aggregate import Note
from notebook.dao import NoteRepository
from notebook.dao.delayed_persist import DelayedPersistNoteRepository
from .event import APPLICATION_TOPIC

OpenNoteCommand = namedtuple('OpenNoteCommand', ['note_id'])
UpdateNotePayloadCommand = namedtuple('UpdateNotePayloadCommand', ['note_id', 'payload'])


class NoteOpened(object):
    def __init__(self, note: Note, payload: str):
        self.note = note
        self.payload = payload

    def __repr__(self):
        return '{cls}[{note}, payload length={len}]'.format(
            cls=self.__class__.__name__,
            len=len(self.payload) if self.payload is not None else '',
            **self.__dict__)


class NoteService(object):
    def __init__(self, note_repository: DelayedPersistNoteRepository, bus: cyrusbus.bus.Bus):
        self.log = logging.getLogger('{m}.{c}'.format(m=self.__class__.__module__, c=self.__class__.__name__))
        self.bus = bus
        self.note_repository = note_repository

        self.bus.subscribe(APPLICATION_TOPIC, self.on_event)

    def load_notebook(self):
        for note in self.note_repository.get_all_notes():  # type: Note
            self.bus.publish(APPLICATION_TOPIC, note.create())

    def on_event(self, bus, event):
        self.log.debug(u'Event received: {event}'.format(event=event))

        if isinstance(event, OpenNoteCommand):  # type: OpenNoteCommand
            self.set_open_note(event.note_id)
        elif isinstance(event, UpdateNotePayloadCommand): # type: UpdateNotePayloadCommand
            self.update_note_payload(event.note_id, event.payload)
        else:
            self.log.debug(u'Unhandled event: {event}'.format(event=event))

    def _publish_event(self, event):
        if event is not None:
            self.bus.publish(APPLICATION_TOPIC, event)

    def save(self):
        """Saves unsaved changes."""
        self.note_repository.persist()

    def set_open_note(self, note_id: str):
        """Sets the currently open note.

        @param note_id: The id of the note that should be open. May be None to indicate the currently open note should be closed.
        """
        if note_id is not None:
            note = self.note_repository.get_note(note_id)
            self.bus.publish(APPLICATION_TOPIC, NoteOpened(note, note.payload))
        else:
            # TODO: Replace with different event
            self.bus.publish(APPLICATION_TOPIC, NoteOpened(None, None))

    def update_note_payload(self, note_id: str, payload: str):
        """Updates the payload of a note.

        @param note_id: The id of the note to update.
        @param payload: The new payload.
        """
        note = self.note_repository.get_note(note_id)
        event = note.set_payload(payload)
        self._publish_event(event)

        # TODO: This should be done by another class reacting to the event
        if event is not None:
            self.note_repository.add_or_update_note(note)
