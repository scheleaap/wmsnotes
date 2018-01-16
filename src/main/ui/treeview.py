# -*- coding: utf-8 -*-

import logging

import cyrusbus
from gi.repository import Gdk, Gtk

from application.note import NoteOpened, OpenNoteCommand
from application.event import APPLICATION_TOPIC
from notebook.aggregate import NoteCreated, FolderPath, NotebookNode

__all__ = [
    'NotebookTreeStore',
]

CONTENT_NODE_TYPE = 'content-node'
FOLDER_NODE_TYPE = 'folder-node'


class NotebookTreeStore(Gtk.TreeStore):
    def __init__(self, bus: cyrusbus.bus.Bus):
        super().__init__(
            str,  # type
            str,  # path element
            str,  # title
            str,  # node_id (only if type == CONTENT_NODE_TYPE)
        )
        self.log = logging.getLogger('{m}.{c}'.format(m=self.__class__.__module__, c=self.__class__.__name__))
        bus.subscribe(APPLICATION_TOPIC, self.on_event)

    @staticmethod
    def create_folder_node_row(path_element: str, title: str):
        return [FOLDER_NODE_TYPE, path_element, title, None]

    @staticmethod
    def create_content_node_row(node_id: str, path_element: str, title: str):
        return [CONTENT_NODE_TYPE, path_element, title, node_id]

    def ensure_folder_exists_and_return_iter(self, remaining_path_elements, parent_iter: Gtk.TreeIter = None):
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
                    self.create_folder_node_row(
                        path_element=current_path_element,
                        title=current_path_element
                    )
                )

            return self.ensure_folder_exists_and_return_iter(
                remaining_path_elements=remaining_path_elements[1:],
                parent_iter=current_child_iter
            )

    def get_iter_from_path_elements(self, remaining_path_elements, parent_iter: Gtk.TreeIter = None):
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

            if current_child_iter is not None:
                return self.get_iter_from_path_elements(
                    remaining_path_elements=remaining_path_elements[1:],
                    parent_iter=current_child_iter
                )
            else:
                raise RuntimeError('Path not found')

    def get_node_id_from_iter(self, iter: Gtk.TreeIter):
        return self.get(iter, 3)[0]

    @staticmethod
    def get_path_elements_for_content_node_from_notebook_node(node: NotebookNode):
        return node.folder_path.elements + [node.title]

    @staticmethod
    def get_path_elements_for_folder_node_from_notebook_node(node: NotebookNode):
        return node.folder_path.elements

    def on_event(self, bus, event, *args, **kwargs):
        self.log.debug(u'Event received: {event}'.format(event=event))

        if isinstance(event, NoteCreated):  # type: NoteCreated
            NoteCreatedHandler.handle(self, event)
        else:
            self.log.debug(u'Unhandled event: {event}'.format(event=event))


class NoteCreatedHandler(object):
    @staticmethod
    def handle(tree_store: NotebookTreeStore, event: NoteCreated):
        parent_iter = tree_store.ensure_folder_exists_and_return_iter(
            NotebookTreeStore.get_path_elements_for_folder_node_from_notebook_node(event.node))
        tree_store.append(
            parent_iter,
            NotebookTreeStore.create_content_node_row(
                node_id=event.node.node_id,
                path_element=event.node.title,
                title=event.node.title
            )
        )


class SaneExpandCollapseTreeViewHandler(object):
    def __init__(self, tree_view: Gtk.TreeView):
        self.log = logging.getLogger('{m}.{c}'.format(m=self.__class__.__module__, c=self.__class__.__name__))
        tree_view.connect('key-press-event', self.on_key_press_event)

    def get_selected_item_path(self, tree_view: Gtk.TreeView, tree_model: Gtk.TreeModel):
        (selected_item_path, _) = tree_view.get_cursor()
        if selected_item_path is not None:
            selected_item_iter = tree_model.get_iter(selected_item_path)
        else:
            tree_selection = tree_view.get_selection()  # type: Gtk.TreeSelection
            (_, selected_item_iter) = tree_selection.get_selected()  # type: Gtk.TreeModel, Gtk.TreeIter
            selected_item_path = tree_model.get_path(selected_item_iter)
        return selected_item_iter, selected_item_path

    def on_key_press_event(self, tree_view: Gtk.TreeView, event: Gdk.EventKey):
        if (event.keyval == Gdk.KEY_Right or event.keyval == Gdk.KEY_KP_Right) and event.state == 0:
            self.on_key_right(tree_view)
        elif (event.keyval == Gdk.KEY_Left or event.keyval == Gdk.KEY_KP_Left) and event.state == 0:
            self.on_key_left(tree_view)

    def on_key_left(self, tree_view):
        tree_model = tree_view.get_model()  # type: Gtk.TreeModel
        selected_item_iter, selected_item_path = \
            self.get_selected_item_path(tree_view, tree_model)  # type: Gtk.TreeIter, Gtk.TreePath
        if tree_view.row_expanded(selected_item_path):
            tree_view.collapse_row(selected_item_path)
        else:
            parent_iter = tree_model.iter_parent(selected_item_iter)
            if parent_iter is not None:
                parent_path = tree_model.get_path(parent_iter)
                tree_view.set_cursor(parent_path)

    def on_key_right(self, tree_view):
        tree_model = tree_view.get_model()  # type: Gtk.TreeModel
        selected_item_iter, selected_item_path = \
            self.get_selected_item_path(tree_view, tree_model)  # type: Gtk.TreeIter, Gtk.TreePath

        if not tree_view.row_expanded(selected_item_path):
            tree_view.expand_row(selected_item_path, open_all=False)
        elif tree_model.iter_has_child(selected_item_iter):
            first_child_iter = tree_model.iter_children(selected_item_iter)  # type: Gtk.TreeIter
            first_child_path = tree_model.get_path(first_child_iter)
            tree_view.set_cursor(first_child_path)


class NotebookTreeViewHandler(object):
    def __init__(
            self,
            bus: cyrusbus.bus.Bus,
            tree_store: NotebookTreeStore,
            tree_view: Gtk.TreeView,
            **kwargs):

        self.log = logging.getLogger('{m}.{c}'.format(m=self.__class__.__module__, c=self.__class__.__name__))
        self.bus = bus
        # self.tree_store = tree_store
        self.tree_view = tree_view

        self.tree_view.get_selection().connect('changed', self.on_selection_changed)
        # bus.subscribe(APPLICATION_TOPIC, self.on_application_event)

    # def on_application_event(self, bus, event, *args, **kwargs):
    #     self.log.debug(u'Event received: {event}'.format(event=event))
    #
    #     if isinstance(event, NoteOpened):  # type: NoteOpened
    #         self.tree_store.get_iter_from_path_elements(
    #             NotebookTreeStore.get_path_elements_for_content_node_from_notebook_node(event.node))
    #     else:
    #         self.log.debug(u'Unhandled event: {event}'.format(event=event))

    def on_selection_changed(self, tree_selection: Gtk.TreeSelection):
        self.log.debug(u'Selection changed')
        (tree_model, iter) = tree_selection.get_selected()  # type: NotebookTreeStore, Gtk.TreeIter
        if iter is not None:
            node_id = tree_model.get_node_id_from_iter(iter)
        else:
            node_id = None
        self._publish(OpenNoteCommand(node_id))

    def _publish(self, object):
        self.bus.publish(APPLICATION_TOPIC, object)
