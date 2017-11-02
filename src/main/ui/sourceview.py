import logging

import cyrusbus
from gi.repository import GtkSource

import application.event
from application.controller import OpenNodeChanged, Controller
from notebook.storage import NotebookStorage


class SourceHandler(object):
    """Connects and controls a GtkSource.View and a GtkSource.Buffer.

    @ivar current_node_id: The id of the current node.
    """

    def __init__(
            self,
            bus: cyrusbus.bus.Bus,
            controller: Controller,
            notebook_storage: NotebookStorage,
            source_view: GtkSource.View,
    ):
        self.log = logging.getLogger('{m}.{c}'.format(m=self.__class__.__module__, c=self.__class__.__name__))
        self.controller = controller
        self.notebook_storage = notebook_storage
        self.source_view = source_view
        self.source_buffer = source_view.get_buffer()  # type: GtkSource.Buffer
        self.current_node_id = None

        self._on_buffer_changed_handler_id = self.source_buffer.connect('changed', self.on_buffer_changed)
        bus.subscribe(application.event.APPLICATION_TOPIC, self.on_application_event)

    def on_application_event(self, bus, event):
        self.log.debug(u'Event received: {event}'.format(event=event))

        if isinstance(event, OpenNodeChanged):  # type: OpenNodeChanged
            with self.source_buffer.handler_block(self._on_buffer_changed_handler_id):
                if event.node is not None:
                    self.current_node_id = event.node.node_id
                    self.source_buffer.set_text(event.payload)
                    self.source_buffer.begin_not_undoable_action()
                    self.source_buffer.end_not_undoable_action()
                    self.source_view.set_sensitive(True)
                else:
                    self.current_node_id = None
                    self.source_buffer.set_text('')
                    self.source_view.set_sensitive(False)
        else:
            self.log.debug(u'Unhandled event: {event}'.format(event=event))

    def on_buffer_changed(self, *args, **kwargs):
        payload = self.source_buffer.get_text(
            self.source_buffer.get_start_iter(),
            self.source_buffer.get_end_iter(),
            include_hidden_chars=False,
        )
        self.controller.update_node_payload(self.current_node_id, payload)
