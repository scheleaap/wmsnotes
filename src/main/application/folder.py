# -*- coding: utf-8 -*-
import logging

import cyrusbus.bus

from notebook.aggregate import Note
from .event import APPLICATION_TOPIC


# class FolderOpened(object):
#     def __init__(self, node: Note):
#         self.node = node
#
#     def __repr__(self):
#         return '{cls}[{node}]'.format(cls=self.__class__.__name__, **self.__dict__)


class FolderService(object):
    def __init__(self, bus: cyrusbus.bus.Bus):
        self.log = logging.getLogger('{m}.{c}'.format(m=self.__class__.__module__, c=self.__class__.__name__))
        self.bus = bus
        bus.subscribe(APPLICATION_TOPIC, self.on_event)

    def _publish_event(self, event):
        if event is not None:
            self.bus.publish(APPLICATION_TOPIC, event)

    # def set_open_node(self, node_id: str):
    #     """Sets the currently open node.
    #
    #     @param node_id: The id of the node that should be open. May be None to indicate the currently open node should be closed.
    #     """
    #     if node_id is not None:
    #         node = self.note_repository.get_node(node_id)
    #         self.bus.publish(APPLICATION_TOPIC, NoteOpened(node, node.payload))
    #     else:
    #         # TODO: Replace with different event
    #         self.bus.publish(APPLICATION_TOPIC, NoteOpened(None, None))

    def on_event(self, bus, event):
        self.log.debug(u'Event received: {event}'.format(event=event))

        # if isinstance(event, NoteOpened):  # type: NoteOpened
        #     with self.source_buffer.handler_block(self._on_buffer_changed_handler_id):
        #         if event.node is not None:
        #             self.set_note(event)
        #         else:
        #             self.clear()
        # else:
        #     self.log.debug(u'Unhandled event: {event}'.format(event=event))
