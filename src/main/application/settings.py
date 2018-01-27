import configparser
import enum
import logging
import os.path
from collections import namedtuple

import cyrusbus

from application.event import APPLICATION_TOPIC

__all__ = [
    'LayoutRequestedEvent'
    'Settings',
    'SettingsController',
    'SettingsRepository'
]

EDITOR_VIEWER_SPLIT_POSITION_KEY = 'editor_viewer_split_position'
MAIN_SPLIT_POSITION_KEY = 'main_split_position'
WINDOW_STATE_KEY = 'window_state'
WINDOW_SIZE_AND_LOCATION_KEY = 'window_size_and_location'

WindowSizeAndLocation = namedtuple('WindowSizeAndLocation', ['width', 'height', 'left', 'top'])


@enum.unique
class WindowState(enum.Enum):
    MAXIMIZED = 'maximized'
    NORMAL = 'normal'


class LayoutRequestedEvent:
    def __init__(
            self,
            window_size_and_location: WindowSizeAndLocation,
            window_state: WindowState,
            main_split_position: int,
            editor_viewer_split_position: int
    ):
        self.main_split_position = main_split_position
        self.editor_viewer_split_position = editor_viewer_split_position
        self.window_size_and_location = window_size_and_location
        self.window_state = window_state


class Settings(LayoutRequestedEvent):  # Refactor inheritance if needed
    def __init__(
            self,
            window_size_and_location: WindowSizeAndLocation,
            window_state: WindowState,
            main_split_position: int,
            editor_viewer_split_position: int
    ):
        super().__init__(
            window_size_and_location,
            window_state,
            main_split_position,
            editor_viewer_split_position
        )


class SettingsRepository:
    def __init__(self, config_file_path):
        """Constructor.

        @param config_file_path: The path to the configuration file.
        """
        self.log = logging.getLogger('{m}.{c}'.format(m=self.__class__.__module__, c=self.__class__.__name__))
        self.config_file_path = config_file_path

        self.log.debug(u'config_file_path={0}'.format(self.config_file_path))

    def ensure_directory_exists(self):
        dir_path = os.path.dirname(self.config_file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def load(self) -> Settings:
        config = configparser.ConfigParser()
        # It is possible to pass a list of files to config.read().
        config.read([self.config_file_path], encoding='utf-8')
        settings = Settings(
            window_size_and_location=self._read_and_parse_window_size_and_location(
                config, 'DEFAULT', WINDOW_SIZE_AND_LOCATION_KEY, fallback=None),
            window_state=self._read_and_parse_enum(
                config, 'DEFAULT', WINDOW_STATE_KEY, WindowState, WindowState.NORMAL),
            main_split_position=config.getint(
                'DEFAULT', MAIN_SPLIT_POSITION_KEY, fallback=300),
            editor_viewer_split_position=config.getint(
                'DEFAULT', EDITOR_VIEWER_SPLIT_POSITION_KEY, fallback=400),
        )
        return settings

    def _read_and_parse_enum(self, config, section, key, enum_class, default):
        try:
            return enum_class[config[section].get(key, default.value)]
        except ValueError:
            return default

    def _read_and_parse_window_size_and_location(self, config, section, key, fallback) -> WindowSizeAndLocation:
        raw_value = config[section].get(key, None)
        if raw_value is None:
            return None
        try:
            int_values = [int(v.strip()) for v in raw_value.split(',')]
        except ValueError:
            return None
        if len(int_values) != 4:
            return None
        return WindowSizeAndLocation(*int_values)

    def save(self, settings: Settings):
        self.ensure_directory_exists()
        config = configparser.ConfigParser()
        config['DEFAULT'] = {}
        if settings.window_size_and_location is not None:
            config['DEFAULT'][WINDOW_SIZE_AND_LOCATION_KEY] = self._serialize_window_size_and_location(
                settings.window_size_and_location)
        if settings.window_state is not None:
            config['DEFAULT'][WINDOW_STATE_KEY] = settings.window_state.name
        if settings.main_split_position is not None:
            config['DEFAULT'][MAIN_SPLIT_POSITION_KEY] = str(settings.main_split_position)
        if settings.editor_viewer_split_position is not None:
            config['DEFAULT'][EDITOR_VIEWER_SPLIT_POSITION_KEY] = str(settings.editor_viewer_split_position)
        with open(self.config_file_path, 'w', encoding='utf-8') as f:
            config.write(f)

        def _serialize_window_size_and_location(self, window_size_and_location: WindowSizeAndLocation) -> str:
            if window_size_and_location is None:
                return None
            return ','.join([
                window_size_and_location.width,
                window_size_and_location.height,
                window_size_and_location.left,
                window_size_and_location.top
            ])


class SettingsController:
    def __init__(self, settings_repository: SettingsRepository, bus: cyrusbus.bus.Bus):
        self.bus = bus
        self.repository = settings_repository

    def load_settings(self):
        settings = self.repository.load()
        self.publish_event(settings)

    # TODO: Rename to "update" once settings are not flushed to disk immediately anymore
    def update_and_save(self, f):
        settings = self.repository.load()
        f(settings)
        self.repository.save(settings)

    def publish_event(self, event):
        if event is not None:
            self.bus.publish(APPLICATION_TOPIC, event)
