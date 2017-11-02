# -*- coding: utf-8 -*-
"""File system storage."""

from __future__ import absolute_import

import io
import hashlib
import logging
import os
import shutil
import xml.etree.ElementTree as et

from . import *
from ..aggregate import NotebookNode, FolderPath

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

    def get_all_nodes(self):
        self.log.debug(u'Loading all nodes')

        def handle_error(e):
            raise e

        for (dirpath, dirnames, filenames) in os.walk(self.dir, onerror=handle_error):
            dirpath = os.path.relpath(dirpath, self.dir)
            for filename in filenames:  # type: str
                if filename.endswith('.md'):
                    node_id = os.path.normpath(os.path.join(dirpath, filename))
                    self.log.debug(u'Found a node with id "{node_id}" in {path}'.format(node_id=node_id, path=dirpath))
                    yield self.get_node(node_id)

    def get_node(self, node_id):
        self.log.debug(u'Loading node {node_id}'.format(node_id=node_id))
        if not self.has_node(node_id):
            raise NodeDoesNotExistError()

        return self._read_node(node_id)

    # def _get_node_directory_path(self, node_id):
    #     return os.path.join(self.dir, node_id)

    def _get_node_file_path(self, node_id):
        return os.path.normpath(os.path.join(self.dir, node_id))

    # def _get_notebook_file_path(self):
    #     return os.path.join(self.dir, 'notebook.xml')

    def get_node_payload(self, node_id, payload_name):
        self.log.debug(u'Loading payload "{name}" of node {node_id}'.format(node_id=node_id, name=payload_name))
        if not self.has_node(node_id):
            raise NodeDoesNotExistError(node_id)
        # if not self.has_node_payload(node_id, payload_name):
        #     raise PayloadDoesNotExistError(node_id, payload_name)

        return io.open(self._get_node_payload_file_path(node_id, payload_name), mode='rb')

    def _get_node_payload_file_path(self, node_id, payload_name):
        # return os.path.join(self.dir, node_id, 'payload', payload_name)
        return self._get_node_file_path(node_id)

    def has_node(self, node_id):
        return os.path.exists(self._get_node_file_path(node_id))

    # def has_node_payload(self, node_id, payload_name):
    #     return os.path.exists(self._get_node_payload_file_path(node_id, payload_name))

    def _read_node(self, node_id):
        """Reads a node.

        @param node_id: The id of the node.
        @return: A NotebookNode.
        """
        path = os.path.dirname(node_id)
        title = os.path.basename(node_id)[:-3]
        return NotebookNode(
            node_id=node_id,
            title=title,
            folder_path=FolderPath.from_string(path))

    def __repr__(self):
        return '{cls}[{dir}]'.format(cls=self.__class__.__name__, **self.__dict__)
