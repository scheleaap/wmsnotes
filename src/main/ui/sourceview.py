import logging

import cyrusbus
from gi.repository import GtkSource

from application.event import APPLICATION_TOPIC
from application.note import NoteOpened, UpdateNodePayloadCommand


class SourceHandler(object):
    """Connects and controls a GtkSource.View and a GtkSource.Buffer.

    @ivar current_node_id: The id of the current node.
    """

    def __init__(
            self,
            bus: cyrusbus.bus.Bus,
            source_view: GtkSource.View,
    ):
        self.log = logging.getLogger('{m}.{c}'.format(m=self.__class__.__module__, c=self.__class__.__name__))
        self.bus = bus
        self.source_view = source_view
        self.source_buffer = source_view.get_buffer()  # type: GtkSource.Buffer
        self.current_node_id = None

        self.clear()
        self._on_buffer_changed_handler_id = self.source_buffer.connect('changed', self.on_buffer_changed)
        self.bus.subscribe(APPLICATION_TOPIC, self.on_application_event)

    def clear(self):
        self.current_node_id = None
        self.source_buffer.set_text('')
        self.source_view.set_sensitive(False)
        self.source_view.hide()

    def on_application_event(self, bus, event):
        self.log.debug(u'Event received: {event}'.format(event=event))

        if isinstance(event, NoteOpened):  # type: NoteOpened
            with self.source_buffer.handler_block(self._on_buffer_changed_handler_id):
                if event.node is not None:
                    self.set_note(event)
                else:
                    self.clear()
        else:
            self.log.debug(u'Unhandled event: {event}'.format(event=event))

    def on_buffer_changed(self, *args, **kwargs):
        payload = self.source_buffer.get_text(
            self.source_buffer.get_start_iter(),
            self.source_buffer.get_end_iter(),
            include_hidden_chars=False,
        )
        self._publish(UpdateNodePayloadCommand(self.current_node_id, payload))

    def _publish(self, object):
        self.bus.publish(APPLICATION_TOPIC, object)

    def set_note(self, event: NoteOpened):
        self.current_node_id = event.node.node_id
        self.source_buffer.set_text(event.node.payload)
        self.source_buffer.begin_not_undoable_action()
        self.source_buffer.end_not_undoable_action()
        self.source_view.set_sensitive(True)
        self.source_view.show()
