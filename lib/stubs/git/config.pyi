import abc
from collections import OrderedDict
from typing import Any, Optional, TypeVar, List, Tuple, Type, Pattern, Sequence, Union, Literal, overload

from pathlib import Path

from .util import LockFile

_Path = Union[str, Path]

_K = TypeVar('_K')
_V = TypeVar('_V')
_D = TypeVar('_D')

_ConfigLevel = Literal['system', 'user', 'global', 'repository']

class MetaParserBuilder(abc.ABCMeta):
    def __new__(cls, name: Any, bases: Any, clsdict: Any) -> Any: ...

class SectionConstraint:
    def __init__(self, config: GitConfigParser, section: str) -> None: ...
    def __del__(self) -> None: ...
    def __getattr__(self, attr: str) -> Any: ...
    @property
    def config(self) -> GitConfigParser: ...
    def release(self) -> None: ...
    def __enter__(self) -> SectionConstraint: ...
    def __exit__(self, exception_type: Any, exception_value: Any, traceback: Any) -> None: ...

class _OMD(OrderedDict[_K, _V]):
    def __setitem__(self, key: _K, value: _V) -> None: ...
    def add(self, key: _K, value: _V) -> None: ...
    def setall(self, key: _K, values: List[_V]) -> None: ...
    def __getitem__(self, key: _K) -> _V: ...
    def getlast(self, key: _K) -> _V: ...
    def setlast(self, key: _K, value: _V) -> None: ...
    def get(self, key: _K, default: Optional[_V] = ...) -> Optional[_V]: ...  # type: ignore[override]
    def getall(self, key: _K) -> List[_V]: ...
    def items(self) -> List[Tuple[_K, _V]]: ...  # type: ignore[override]
    def items_all(self) -> List[Tuple[_K, List[_V]]]: ...

class GitConfigParser:
    t_lock: Type[LockFile] = ...
    re_comment: Pattern[str] = ...
    OPTVALUEONLY: Pattern[str] = ...
    OPTCRE: Pattern[str] = ...
    def __init__(self, file_or_files: Union[Sequence[_Path], _Path, None] = ..., read_only: bool = ..., merge_includes: bool = ..., config_level: Optional[_ConfigLevel] = ...) -> None: ...
    def __del__(self) -> None: ...
    def __enter__(self) -> GitConfigParser: ...
    def __exit__(self, exception_type: Any, exception_value: Any, traceback: Any) -> None: ...
    def release(self) -> None: ...
    def optionxform(self, optionstr: str) -> str: ...
    def read(self) -> None: ...
    def items(self, section_name: str) -> List[Tuple[str, str]]: ...
    def items_all(self, section_name: str) -> List[Tuple[str, List[str]]]: ...
    def write(self) -> None: ...
    def add_section(self, section: str) -> None: ...
    @property
    def read_only(self) -> bool: ...
    @overload
    def get_value(self, section: str, option: str, default: _D = ...) -> Union[str, int, float, _D]: ...
    @overload
    def get_value(self, section: str, option: str) -> Union[str, int, float]: ...  # type: ignore[misc]
    @overload
    def get_values(self, section: str, option: str, default: _D = ...) -> List[Union[str, int, float, _D]]: ...
    @overload
    def get_values(self, section: str, option: str) -> List[Union[str, int, float]]: ...  # type: ignore[misc]
    def set_value(self, section: str, option: str, value: Any) -> GitConfigParser: ...
    def add_value(self, section: str, option: str, value: Any) -> GitConfigParser: ...
    def rename_section(self, section: str, new_name: str) -> GitConfigParser: ...
