from typing import Sequence

import attr

from models.base import Model

@attr.s(auto_attribs=True)
class Module(Model):
    name : str
    uses : int

@attr.s(auto_attribs=True)
class MostUsedRoles(Model):
    name : str
    modules : Sequence[Module]

