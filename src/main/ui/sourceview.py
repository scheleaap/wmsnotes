import logging

import cyrusbus
from gi.repository import GtkSource

import application.event
from application.controller import OpenNodeChanged
from notebook.storage import NotebookStorage


class ContentNodeSourceBuffer(GtkSource.Buffer):
    def __init__(self, bus: cyrusbus.bus.Bus, notebook_storage: NotebookStorage, **kwargs):
        super().__init__(**kwargs)
        self.log = logging.getLogger('{m}.{c}'.format(m=self.__class__.__module__, c=self.__class__.__name__))
        self.notebook_storage = notebook_storage
        bus.subscribe(application.event.APPLICATION_TOPIC, self.on_application_event)

    def on_application_event(self, bus, event):
        self.log.debug(u'Event received: {event}'.format(event=event))

        if isinstance(event, OpenNodeChanged):  # type: OpenNodeChanged
            if event.node is not None:
                self.set_text(event.payload)
            else:
                self.set_text('')
        else:
            self.log.debug(u'Unhandled event: {event}'.format(event=event))
