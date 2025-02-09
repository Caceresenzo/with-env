import os
import threading
import typing

import watchdog.events
import watchdog.observers
import watchdog.utils
import watchdog.utils.event_debouncer

from .execute import RestartableProgramExecutor


class EventHandler(watchdog.events.FileSystemEventHandler):

    def __init__(self, event_debouncer: watchdog.utils.event_debouncer.EventDebouncer):
        self._event_debouncer = event_debouncer

    def on_modified(self, event: watchdog.events.FileModifiedEvent) -> None:
        self._event_debouncer.handle_event(event)


class FileObserver:

    def __init__(
        self,
        executor: RestartableProgramExecutor,
    ):
        self._executor = executor

        self._on_update = threading.Condition()

        self._event_debouncer = watchdog.utils.event_debouncer.EventDebouncer(1, self._on_file_changed)
        self._event_handler = EventHandler(self._event_debouncer)

        self._event_debouncer.start()

    def _on_file_changed(self, _):
        with self._on_update:
            self._on_update.notify()

    def run(
        self,
        env_files: typing.List[str]
    ):
        observer = watchdog.observers.Observer()

        for env_file in env_files:
            if os.path.exists(env_file):
                observer.schedule(self._event_handler, env_file)

        observer.start()

        try:
            while True:
                with self._on_update:
                    must_restart = self._on_update.wait(0.5)

                if must_restart:
                    self._executor.start()
        except KeyboardInterrupt:
            print("with-env: exiting...")

            observer.stop()
            observer.join()
