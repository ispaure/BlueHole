"""Reload state machine with an explicit barrier for native ownership cleanup.

The caller polls tick() on Blender's main thread and supplies the old runtime's
cleanup callback before purging modules. No new runtime starts while the old
runtime still has pending ownership. File transport is separate from lifecycle.
"""
from time import monotonic


class ReloadTransaction:
    def __init__(self, installation, *, disable, purge, enable, readiness, complete,
                 clock=monotonic, timeout=30):
        self.installation = installation
        self.disable, self.purge, self.enable = disable, purge, enable
        self.readiness, self.on_complete = readiness, complete
        self.clock, self.timeout = clock, timeout
        self.phase = 'idle'
        self.deadline = 0
        self.error = ''
        self.restoring = False
        self.done = False
        self.cleanup = None

    def begin(self):
        try:
            self.installation.prepare()
        except Exception as error:
            self.error = str(error)
            self.complete()
            return
        try:
            self._unload()
        except Exception as error:
            self._stop(error)

    def _unload(self):
        self.phase = 'cleanup'
        self.deadline = self.clock() + self.timeout
        self.cleanup = self.disable()

    def tick(self):
        if self.done:
            return None
        try:
            if self.phase == 'cleanup':
                if not self.cleanup():
                    if self.clock() >= self.deadline:
                        self._stop(RuntimeError('Keymap cleanup timed out; no new runtime was enabled'))
                    return None if self.done else 0.1
                if self.restoring:
                    self.installation.rollback()
                else:
                    self.installation.publish()
                self.purge()
                self.enable()
                self.phase = 'ready'
                self.deadline = self.clock() + self.timeout
            ready, error = self.readiness()
            if error:
                raise RuntimeError(error)
            if ready:
                if not self.restoring:
                    self.installation.finish()
                self.complete()
            elif self.clock() >= self.deadline:
                raise RuntimeError('Blue Hole initialization timed out')
        except Exception as error:
            self.rollback(error)
        return None if self.done else 0.1

    def rollback(self, error):
        if self.restoring:
            self._stop(error)
            return
        self.error = str(error)
        self.restoring = True
        try:
            self._unload()
        except Exception as recovery:
            self._stop(recovery)

    def _stop(self, error):
        self.error = '; '.join(filter(None, (self.error, str(error))))
        try:
            self.installation.rollback()
        except Exception as recovery:
            self.error += '; file recovery: ' + str(recovery)
        self.complete(recovered=False)

    def complete(self, recovered=True):
        self.done = True
        self.phase = 'complete' if recovered else 'stopped'
        self.on_complete(recovered)
