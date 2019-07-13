from abc import ABCMeta
from abc import abstractstaticmethod


class BasePlugin(metaclass=ABCMeta):

    @staticmethod
    def should_run(request_sequence, response_sequence):
        return True

    @abstractstaticmethod
    def is_vulnerable(request_sequence, response_sequence):
        pass
