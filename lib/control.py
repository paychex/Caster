from dragonfly import RecognitionHistory, Grammar
from dragonfly.timer import _Timer

from lib import settings


MULTI_CLIPBOARD={}

DICTATION_CACHE=RecognitionHistory(10)
DICTATION_CACHE.register()
PRESERVED_CACHE=None

TIMER_MANAGER=_Timer(1)

RECORDED_MACROS_GRAMMAR = Grammar("recorded_macros")


def print_startup_message():
    print "*- Starting "+settings.SOFTWARE_NAME+" -*"







