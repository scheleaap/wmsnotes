# -*- coding: utf-8 -*-

import cyrusbus.bus

from .aggregate import NotebookNode
from .event import NODE_EVENTS_TOPIC


class Controller(object):
    def __init__(self, notebook_storage, bus: cyrusbus.bus.Bus):
        self.bus = bus
        self.notebook_storage = notebook_storage

    def load_notebook(self):
        for node in self.notebook_storage.get_all_nodes():  # type: NotebookNode
            self.bus.publish(NODE_EVENTS_TOPIC, node.create())
