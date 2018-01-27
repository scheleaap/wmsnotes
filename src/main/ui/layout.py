import logging

import cyrusbus
from gi.repository import Gdk, Gtk

import application.event
from application.settings import Settings, SettingsController, LayoutRequestedEvent, WindowState


class LayoutHandler(object):
    """Controls the layout of a the application.

    - Window state, size, position
    - Split pane positions
    """

    def __init__(
            self,
            bus: cyrusbus.bus.Bus,
            settings_controller: SettingsController,
            window: Gtk.Window,
            main_split_pane: Gtk.Paned,
            editor_viewer_split_pane: Gtk.Paned
    ):
        self.log = logging.getLogger('{m}.{c}'.format(m=self.__class__.__module__, c=self.__class__.__name__))
        self.main_split_pane = main_split_pane
        self.settings_controller = settings_controller  # type: SettingsController
        self.editor_viewer_split_pane = editor_viewer_split_pane
        self.window = window

        self._on_window_state_changed_handler_id = self.window.connect(
            'window-state-event', self.on_window_state_changed)
        self._on_position_changed_handler_id_main = self.main_split_pane.connect(
            'notify::position', self.on_position_changed_main)
        self._on_position_changed_handler_id_editor_viewer = self.editor_viewer_split_pane.connect(
            'notify::position', self.on_position_changed_editor_viewer)
        bus.subscribe(application.event.APPLICATION_TOPIC, self.on_event)

    def on_event(self, bus, event):
        self.log.debug(u'Event received: {event}'.format(event=event))

        if isinstance(event, LayoutRequestedEvent):  # type: LayoutRequestedEvent

            with self.main_split_pane.handler_block(self._on_position_changed_handler_id_main), \
                 self.editor_viewer_split_pane.handler_block(self._on_position_changed_handler_id_editor_viewer), \
                 self.window.handler_block(self._on_window_state_changed_handler_id):

                if event.window_state == WindowState.MAXIMIZED:
                    self.window.maximize()
                elif event.window_state == WindowState.NORMAL:
                    self.window.unmaximize()
                    self.window.deiconify()

                if event.window_size_and_location is not None:
                    self.window.move(event.window_size_and_location.left, event.window_size_and_location.top)
                    self.window.resize(event.window_size_and_location.width,
                                       event.window_size_and_location.height)
                if event.main_split_position is not None:
                    self.main_split_pane.set_position(event.main_split_position)
                if event.editor_viewer_split_position is not None:
                    self.editor_viewer_split_pane.set_position(event.editor_viewer_split_position)
        else:
            self.log.debug(u'Unhandled event: {event}'.format(event=event))

    def on_position_changed_editor_viewer(self, *args, **kwargs):
        position = self.editor_viewer_split_pane.get_position()

        def f(settings: Settings):
            settings.editor_viewer_split_position = position

        self.settings_controller.update_and_save(f)

    def on_position_changed_main(self, *args, **kwargs):
        position = self.main_split_pane.get_position()

        def f(settings: Settings):
            settings.main_split_position = position

        self.settings_controller.update_and_save(f)

    def on_window_state_changed(self, _, event: Gdk.EventWindowState):
        print(event.changed_mask & Gdk.WindowState.MAXIMIZED)
        if event.changed_mask & Gdk.WindowState.MAXIMIZED:
            def f(settings: Settings):
                if event.new_window_state & Gdk.WindowState.MAXIMIZED:
                    settings.window_state = WindowState.MAXIMIZED
                else:
                    settings.window_state = WindowState.NORMAL

            self.settings_controller.update_and_save(f)
