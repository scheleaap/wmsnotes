# -*- coding: utf-8 -*-

import logging

import cyrusbus
from gi.repository import Gtk

from notebook.aggregate import NodeCreated, FolderPath, NotebookNode
from notebook.event import NODE_EVENTS_TOPIC

__all__ = [
    'NotebookTreeStore',
]

CONTENT_NODE_TYPE = 'content-node'
FOLDER_NODE_TYPE = 'folder-node'


# class TreePath(object):
#     @staticmethod
#     def from_node(node: NotebookNode):
#         return TreePath(node.folder_path + [node.title])
#
#     def __init__(self, elements):
#         self.elements = elements
#
#     def __repr__(self):
#         return '{cls}[{path}}]'.format(
#             cls=self.__class__.__name__,
#             path='/'.join(self.elements),
#             **self.__dict__
#         )


class NotebookTreeStore(Gtk.TreeStore):
    def __init__(self, bus: cyrusbus.bus.Bus):
        super().__init__(
            str,  # type
            str,  # path element
            str,  # title
            str,  # node_id (only if type == CONTENT_NODE_TYPE)
        )
        self.bus = bus
        self.bus.subscribe(NODE_EVENTS_TOPIC, self.on_event)
        self.log = logging.getLogger('{m}.{c}'.format(m=self.__class__.__module__, c=self.__class__.__name__));

    def ensure_folder_exists_and_return_iter(self, path_elements):
        return self._ensure_folder_exists_and_return_iter(path_elements, None)

    def _ensure_folder_exists_and_return_iter(
            self,
            remaining_path_elements,
            parent_iter: Gtk.TreeIter
    ):
        if len(remaining_path_elements) == 0:
            return parent_iter
        else:
            current_path_element = remaining_path_elements[0]

            if parent_iter is None:
                current_child_iter = self.get_iter_first()
            else:
                current_child_iter = self.iter_children(parent_iter)

            while current_child_iter is not None:
                matches = current_path_element == self.get_value(current_child_iter, 1)
                if matches:
                    break
                else:
                    current_child_iter = self.iter_next(current_child_iter)

            if current_child_iter is None:
                current_child_iter = self.append(
                    parent_iter,
                    self.create_folder_row(
                        path_element=current_path_element,
                        title=current_path_element
                    )
                )

            return self._ensure_folder_exists_and_return_iter(
                remaining_path_elements=remaining_path_elements[1:],
                parent_iter=current_child_iter
            )

    def on_event(self, bus, event, *args, **kwargs):
        self.log.debug(u'Event received: {event}'.format(event=event))

        if isinstance(event, NodeCreated):  # type: NodeCreated
            NodeCreatedHandler.handle(self, event)
        else:
            self.log.debug(u'Unhandled event: {event}'.format(event=event))

    def create_folder_row(self, path_element: str, title: str):
        return [FOLDER_NODE_TYPE, path_element, title, None]


class NodeCreatedHandler(object):
    @staticmethod
    def handle(tree_store: NotebookTreeStore, event: NodeCreated):
        tree_path = event.node.folder_path.elements + [event.node.title]
        parent_iter = tree_store.ensure_folder_exists_and_return_iter(event.node.folder_path.elements)
        tree_store.append(
            parent_iter,
            [
                CONTENT_NODE_TYPE,
                event.node.title,
                event.node.title,
                event.node.node_id,
            ]
        )
