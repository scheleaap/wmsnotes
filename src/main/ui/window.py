import logging

import cyrusbus
from gi.repository import Gtk

import application.event
from application.controller import NoteOpened


class MainWindowHandler(object):
    """Connects and controls a Gtk.Window.

    - Window title
    """

    def __init__(
            self,
            bus: cyrusbus.bus.Bus,
            window: Gtk.Window,
    ):
        self.log = logging.getLogger('{m}.{c}'.format(m=self.__class__.__module__, c=self.__class__.__name__))
        self.window = window

        bus.subscribe(application.event.APPLICATION_TOPIC, self.on_application_event)

        self.set_title(None)

    def on_application_event(self, bus, event):
        self.log.debug(u'Event received: {event}'.format(event=event))

        if isinstance(event, NoteOpened):  # type: NoteOpened
            self.set_title(event.node)
        else:
            self.log.debug(u'Unhandled event: {event}'.format(event=event))

    def set_title(self, node):
        if node is not None:
            self.window.set_title('WMS Notes - {title}'.format(title=node.title))
        else:
            self.window.set_title('WMS Notes')
