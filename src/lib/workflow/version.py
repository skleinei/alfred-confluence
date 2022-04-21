import re


class Version:
    """Mostly semantic versioning.

    The main difference to proper :ref:`semantic versioning <semver>`
    is that this implementation doesn't require a minor or patch version.

    Version strings may also be prefixed with "v", e.g.:

    >>> v = Version('v1.1.1')
    >>> v.tuple
    (1, 1, 1, '')

    >>> v = Version('2.0')
    >>> v.tuple
    (2, 0, 0, '')

    >>> Version('3.1-beta').tuple
    (3, 1, 0, 'beta')

    >>> Version('1.0.1') > Version('0.0.1')
    True
    """

    #: Match version and pre-release/build information in version strings
    match_version = re.compile(r"([0-9\.]+)(.+)?").match

    def __init__(self, vstr):
        """Create new `Version` object.

        Args:
            vstr (basestring): Semantic version string.
        """
        self.vstr = vstr
        self.major = 0
        self.minor = 0
        self.patch = 0
        self.suffix = ""
        self.build = ""
        self._parse(vstr)

    def _parse(self, vstr):
        if vstr.startswith("v"):
            m = self.match_version(vstr[1:])
        else:
            m = self.match_version(vstr)
        if not m:
            raise ValueError(f"Invalid version number: {vstr}")

        version, suffix = m.groups()
        parts = self._parse_dotted_string(version)
        self.major = parts.pop(0)
        if len(parts):
            self.minor = parts.pop(0)
        if len(parts):
            self.patch = parts.pop(0)
        if not len(parts) == 0:
            raise ValueError(f"Invalid version (too long) : {vstr}")

        if suffix:
            # Build info
            idx = suffix.find("+")
            if idx > -1:
                self.build = suffix[idx + 1 :]
                suffix = suffix[:idx]
            if suffix:
                if not suffix.startswith("-"):
                    raise ValueError("Invalid suffix : `{}`. Must start with `-`".format(suffix))
                self.suffix = suffix[1:]

        # wf().logger.debug('version str `{}` -> {}'.format(vstr, repr(self)))

    def _parse_dotted_string(self, s):
        """Parse string ``s`` into list of ints and strings."""
        parsed = []
        parts = s.split(".")
        for p in parts:
            if p.isdigit():
                p = int(p)
            parsed.append(p)
        return parsed

    @property
    def tuple(self):
        """Version number as a tuple of major, minor, patch, pre-release."""
        return (self.major, self.minor, self.patch, self.suffix)

    def __lt__(self, other):
        """Implement comparison."""
        if not isinstance(other, Version):
            raise ValueError(f"Not a Version instance: {other!r}")
        t = self.tuple[:3]
        o = other.tuple[:3]
        if t < o:
            return True
        if t == o:  # We need to compare suffixes
            if self.suffix and not other.suffix:
                return True
            if other.suffix and not self.suffix:
                return False
            return self._parse_dotted_string(self.suffix) < self._parse_dotted_string(other.suffix)
        # t > o
        return False

    def __eq__(self, other):
        """Implement comparison."""
        if not isinstance(other, Version):
            raise ValueError(f"Not a Version instance: {other!r}")
        return self.tuple == other.tuple

    def __ne__(self, other):
        """Implement comparison."""
        return not self.__eq__(other)

    def __gt__(self, other):
        """Implement comparison."""
        if not isinstance(other, Version):
            raise ValueError(f"Not a Version instance: {other!r}")
        return other.__lt__(self)

    def __le__(self, other):
        """Implement comparison."""
        if not isinstance(other, Version):
            raise ValueError(f"Not a Version instance: {other!r}")
        return not other.__lt__(self)

    def __ge__(self, other):
        """Implement comparison."""
        return not self.__lt__(other)

    def __str__(self):
        """Return semantic version string."""
        vstr = f"{self.major}.{self.minor}.{self.patch}"
        if self.suffix:
            vstr += f"-{self.suffix}"
        if self.build:
            vstr += f"+{self.build}"
        return vstr

    def __repr__(self):
        """Return 'code' representation of `Version`."""
        return f"Version('{str(self)}')"
