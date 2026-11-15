"""Editor read-model cache. Catalog snapshots are treated as immutable."""
from dataclasses import dataclass


@dataclass
class PreviewCache:
    draft: object
    serial: int
    catalog: dict
    view: dict
    plan: tuple
    active: dict
    environment: tuple

    @property
    def stamp(self):
        return self.draft, self.serial

    @property
    def token(self):
        return self.environment + (tuple(sorted(self.view['runtime'].items())),)
