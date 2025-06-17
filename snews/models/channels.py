# -*- coding: utf-8 -*-
__all__ = ["ChannelType"]

from enum import Enum

class ChannelType(Enum):
    IBD = "Inverse Beta Decay"
    PES = "Neutrino-proton Elastic Scattering"
    EES = "Neutrino-electron Elastic Scattering"
    OTHER = "Other"
