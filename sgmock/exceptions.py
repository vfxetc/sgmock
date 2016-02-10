
class ShotgunError(Exception):
    """Exception for all server logic."""
    pass

class Fault(ShotgunError):
    """Exception for all remote API logic; unused in this mock."""

    _default_code = 999

    @property
    def code(self):
        try:
            return self.args[1]
        except IndexError:
            return self._default_code
