from abc import abstractmethod

import astropy.coordinates as c


class Evaluation:
    def __init__(self, orbit: c.SkyCoord):
        self.orbit = orbit

    @property
    @abstractmethod
    def measure(self) -> float:
        pass

    @abstractmethod
    def plot(self):
        pass
