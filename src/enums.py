from enum import Enum


class Format(Enum):
    BEST = 0
    MP4 = 1
    AUDIO = 2


class Subtitles(Enum):
    OFF = 0
    EMBED = 1
    SRT = 2
    TXT = 3
    SRT_AND_TXT = 4


class SponsorBlock(Enum):
    OFF = 0
    REMOVE = 1
    MARK = 2
