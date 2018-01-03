import logging

import cyrusbus
from gi.repository import GtkSource, WebKit2
import markdown
from markdown.extensions.toc import TocExtension
from markdown.extensions.sane_lists import SaneListExtension
from pymdownx.github import GithubExtension

import application.event
from application.controller import NoteOpened, Controller


class WebViewHandler(object):
    """Connects and controls a WebKit2.WebView.
    """

    def __init__(
            self,
            bus: cyrusbus.bus.Bus,
            controller: Controller,
            web_view: WebKit2.WebView,
    ):
        self.log = logging.getLogger('{m}.{c}'.format(m=self.__class__.__module__, c=self.__class__.__name__))
        self.controller = controller
        self.web_view = web_view

        self.clear()
        bus.subscribe(application.event.APPLICATION_TOPIC, self.on_application_event)

    def clear(self):
        self.web_view.hide()

    def on_application_event(self, bus, event):
        self.log.debug(u'Event received: {event}'.format(event=event))

        if isinstance(event, NoteOpened):  # type: NoteOpened
            if event.node is not None:
                self.set_note(event)
            else:
                self.clear()
        else:
            self.log.debug(u'Unhandled event: {event}'.format(event=event))

    def set_note(self, event):
        html = markdown.markdown(
            event.node.payload,
            tab_length=2,
            extensions=[GithubExtension(), SaneListExtension(), TocExtension()],
            output_format='html5',
        )
        # self.webview.load_uri('file:///D:/Users/.../test.html')
        self.web_view.load_html(
            html,
            # base_uri='file:///D:/Users/.../Python/test/'
        )
        self.web_view.show()
