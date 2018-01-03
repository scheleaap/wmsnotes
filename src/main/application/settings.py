import configparser
import enum
import logging
import os.path

import cyrusbus

from application.event import APPLICATION_TOPIC


@enum.unique
class WindowState(enum.Enum):
    MAXIMIZED = 'maximized'
    NORMAL = 'normal'


class LayoutRequestedEvent:
    def __init__(self, window_state: WindowState, main_split_position: int, editor_viewer_split_position: int):
        self.main_split_position = main_split_position
        self.editor_viewer_split_position = editor_viewer_split_position
        self.window_state = window_state


class Settings(LayoutRequestedEvent):  # Refactor inheritance if needed
    def __init__(self, window_state: WindowState, main_split_position: int, editor_viewer_split_position: int):
        super().__init__(window_state, main_split_position, editor_viewer_split_position)


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
            window_state=self._get_enum(config, 'DEFAULT', 'window_state', WindowState, WindowState.NORMAL),
            main_split_position=config.getint('DEFAULT', 'main_split_position', fallback=300),
            editor_viewer_split_position=config.getint('DEFAULT', 'editor_viewer_split_position', fallback=400),
        )
        return settings

    def _get_enum(self, config, section, key, enum_class, default):
        try:
            return enum_class(config[section].get(key, default.value))
        except ValueError:
            return default

    def save(self, settings: Settings):
        self.ensure_directory_exists()
        config = configparser.ConfigParser()
        config['DEFAULT'] = settings
        with open(self.config_file_path, 'w', encoding='utf-8') as f:
            config.write(f)


class SettingsController:
    def __init__(self, settings_repository: SettingsRepository, bus: cyrusbus.bus.Bus):
        self.bus = bus
        self.repository = settings_repository

    def load_settings(self):
        settings = self.repository.load()
        self.publish_event(settings)

    def save_layout(self):
        """Saves the window layout."""
        self.repository.save(Settings(
            window_state=WindowState.MAXIMIZED,
            main_split_position=0,
            editor_viewer_split_position=0
        ))

    def publish_event(self, event):
        if event is not None:
            self.bus.publish(APPLICATION_TOPIC, event)
