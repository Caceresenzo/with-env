import os
import sys
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

        self._condition = threading.Condition()
        self._program_exit_code = None
        self._must_restart = False

        self._event_debouncer = watchdog.utils.event_debouncer.EventDebouncer(1, self._on_file_changed)
        self._event_handler = EventHandler(self._event_debouncer)

        self._event_debouncer.start()

    def _on_file_changed(self, _):
        with self._condition:
            self._must_restart = True
            self._condition.notify()

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
                timeout = 0.5 if self._executor.running else None
                with self._condition:
                    self._condition.wait(timeout)

                exit_code = self._executor.exited()
                if exit_code is not None:
                    print(f"with-env: program stopped with exit code {exit_code}", file=sys.stderr)

                if self._must_restart:
                    print(f"with-env: changes detected in env file(s), restarting process...", file=sys.stderr)
                    self._executor.start()
                    self._must_restart = False
        except KeyboardInterrupt:
            print("with-env: exiting...", file=sys.stderr)

            observer.stop()
            observer.join()
