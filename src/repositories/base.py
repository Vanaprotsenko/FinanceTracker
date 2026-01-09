from abc import ABC, abstractmethod


class Repository(ABC):

    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass
