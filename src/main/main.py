# -*- coding: utf-8 -*-

import io
import logging
import sys

import cyrusbus
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
gi.require_version('WebKit2', '3.0')
from gi.repository import Gio, GObject, Gtk, GtkSource, WebKit2
import markdown
from markdown.extensions.toc import TocExtension
from markdown.extensions.sane_lists import SaneListExtension
from pymdownx.github import GithubExtension

from application.controller import Controller
from notebook.storage.simple_fs import SimpleFileSystemStorage
import ui.sourceview
import ui.treeview
import ui.window


def initialize_logging():
    # logging.basicConfig(format='%(asctime)s %(levelname)5s %(msg)s [%(pathname)s]', level=logging.DEBUG)
    logging.basicConfig(format='%(asctime)s %(levelname)5s %(msg)s [%(name)s]', level=logging.DEBUG)
    # logging.debug('Debug log message test')
    # logging.info('Info log message test')
    # logging.warning('Warning log message test')
    # logging.error('Error log message test')


class App(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                         application_id='info.maaskant.wmsnotes',
                         flags=Gio.ApplicationFlags.FLAGS_NONE,
                         **kwargs)
        GObject.type_register(GtkSource.View)
        self.bus = cyrusbus.bus.Bus()
        self.notebook_storage = SimpleFileSystemStorage('resources/notebook')
        self.controller = Controller(self.notebook_storage, self.bus)
        self.builder = None  # type: Gtk.Builder
        self.window = None  # type: Gtk.ApplicationWindow
        self.webview = None  # type: WebKit2.WebView

    #    def do_startup(self):
    #        super().do_startup()

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.initialize_builder()
            # self.builder.connect_signals({
            #     'on_load_button_clicked': self.load,
            # })

            self.initialize_tree_view()
            self.initialize_source_view()
            # self.webview = WebKit2.WebView()
            # box = self.builder.get_object('split_pane2')
            # box.add2(self.webview)

            self.window = self.builder.get_object('main-window')  # type: Gtk.ApplicationWindow
            self.window.show_all()
            self.add_window(self.window)

            self.window.set_focus(self.builder.get_object('tree_view'))
            ui.window.MainWindowHandler(self.bus, self.window)

            self.load()

        self.window.present()

    def initialize_builder(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('resources/glade/ui.xml')

    def initialize_source_view(self):
        language_manager = GtkSource.LanguageManager.get_default()
        markdown_language = language_manager.get_language('markdown')
        source_view = self.builder.get_object('source_view')  # type: GtkSource.View
        buffer = source_view.get_buffer()
        buffer.set_language(markdown_language)
        ui.sourceview.SourceHandler(
            bus=self.bus,
            controller=self.controller,
            notebook_storage=self.notebook_storage,
            source_view=source_view
        )

    def initialize_tree_view(self):
        tree_store = ui.treeview.NotebookTreeStore(self.bus)

        tree_view = self.builder.get_object('tree_view')  # type: Gtk.TreeView
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Title', renderer, text=1)
        tree_view.append_column(column)

        tree_view.set_model(tree_store)

        ui.treeview.NotebookTreeViewHandler(
            bus=self.bus,
            controller=self.controller,
            tree_store=tree_store,
            tree_view=tree_view)

    def load(self, *args, **kwargs):
        self.controller.load_notebook()

        # def load_individual_node(self):
        #     data = 'bla'
        #
        #     html = markdown.markdown(
        #         data,
        #         tab_length=2,
        #         extensions=[GithubExtension(), SaneListExtension(), TocExtension()],
        #         output_format='html5',
        #     )
        #     # self.webview.load_uri('file:///D:/Users/Wout/Programma\'s/Python/test/test.html')
        #     self.webview.load_html(html, base_uri='file:///D:/Users/Wout/Programma\'s/Python/test/')


if __name__ == '__main__':
    initialize_logging()
    try:
        app = App()
        app.run(sys.argv)
    except KeyboardInterrupt:
        pass
