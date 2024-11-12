from collections import namedtuple
from typing import Any, Optional, Type, Pattern, Literal, Tuple, Iterator, Union

from pathlib import Path


from git.cmd import Git
from git.db import GitCmdObjectDB
from git.util import IterableList, RemoteProgress
from git.refs.head import Head, HEAD
from git.refs.reference import Reference
from git.refs.tag import TagReference
from git.remote import Remote
from git.objects.commit import Commit

_Path = Union[Path, str]


BlameEntry = namedtuple('BlameEntry', ['commit', 'linenos', 'orig_path', 'orig_linenos'])

_ConfigLevel = Literal['system', 'user', 'global', 'repository']

class Repo:
    DAEMON_EXPORT_FILE: str = ...
    git: Git = ...
    working_dir: str = ...
    git_dir: str = ...
    re_whitespace: Pattern[str] = ...
    re_hexsha_only: Pattern[str] = ...
    re_hexsha_shortened: Pattern[str] = ...
    re_envvars: Pattern[str] = ...
    re_author_committer_start: Pattern[str] = ...
    re_tab_full_line: Pattern[str] = ...
    config_level: Tuple[_ConfigLevel, ...] = ...
    GitCommandWrapperType: Type[Git] = ...
    odb: GitCmdObjectDB = ...
    def __init__(self, path: _Path = ..., odbt: Type[GitCmdObjectDB] = ..., search_parent_directories: bool = ..., expand_vars: bool = ...) -> None: ...
    def __enter__(self) -> Repo: ...
    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None: ...
    def __del__(self) -> None: ...
    def close(self) -> None: ...
    def __eq__(self, rhs: Any) -> bool: ...
    def __ne__(self, rhs: Any) -> bool: ...
    def __hash__(self) -> int: ...
    description: str = ...
    @property
    def working_tree_dir(self) -> str: ...
    @property
    def common_dir(self) -> str: ...
    @property
    def bare(self) -> bool: ...
    @property
    def heads(self) -> IterableList[Head]: ...
    @property
    def references(self) -> IterableList[Reference]: ...
    refs = references
    branches = heads
    @property
    def index(self) -> Any: ...
    @property
    def head(self) -> HEAD: ...
    @property
    def remotes(self) -> IterableList[Remote]: ...
    def remote(self, name: str = ...) -> Remote: ...
    @property
    def submodules(self) -> IterableList[Any]: ...
    def submodule(self, name: str) -> Any: ...
    def create_submodule(self, *args: Any, **kwargs: Any) -> Any: ...
    def iter_submodules(self, *args: Any, **kwargs: Any) -> Any: ...
    def submodule_update(self, *args: Any, **kwargs: Any) -> Any: ...
    @property
    def tags(self) -> IterableList[TagReference]: ...
    def tag(self, path: str) -> TagReference: ...
    def create_head(self, path: str, commit: str = ..., force: bool = ..., logmsg: Optional[str] = ...) -> Head: ...
    def delete_head(self, *heads: Head, **kwargs: Any) -> None: ...
    def create_tag(self, path: str, ref: str = ..., message: Optional[str] = ..., force: bool = ..., **kwargs: Any) -> TagReference: ...
    def delete_tag(self, *tags: TagReference) -> None: ...
    def create_remote(self, name: str, url: str, **kwargs: Any) -> Remote: ...
    def delete_remote(self, remote: str) -> None: ...
    def config_reader(self, config_level: Optional[Any] = ...) -> Any: ...
    def config_writer(self, config_level: str = ...) -> Any: ...
    def commit(self, rev: Optional[str] = ...) -> Commit: ...
    def iter_trees(self, *args: Any, **kwargs: Any) -> Any: ...
    def tree(self, rev: Optional[Any] = ...) -> Any: ...
    def iter_commits(self, rev: Optional[str] = ..., paths: str = ..., **kwargs: Any) -> Iterator[Commit]: ...
    def merge_base(self, *rev: Any, **kwargs: Any) -> Any: ...
    def is_ancestor(self, ancestor_rev: Any, rev: Any) -> Any: ...
    daemon_export: Any = ...
    alternates: Any = ...
    def is_dirty(self, index: bool = ..., working_tree: bool = ..., untracked_files: bool = ..., submodules: bool = ..., path: Optional[Any] = ...) -> bool: ...
    @property
    def untracked_files(self) -> Any: ...
    @property
    def active_branch(self) -> Any: ...
    def blame_incremental(self, rev: Any, file: Any, **kwargs: Any) -> None: ...
    def blame(self, rev: Any, file: Any, incremental: bool = ..., **kwargs: Any) -> Any: ...
    @classmethod
    def init(cls, path: _Path = ..., mkdir: bool = ..., odbt: Any = ..., expand_vars: bool = ..., **kwargs: Any) -> Repo: ...
    def clone(self, path: _Path, progress: Optional[RemoteProgress] = ..., multi_options: Optional[Any] = ..., **kwargs: Any) -> Repo: ...
    @classmethod
    def clone_from(cls, url: str, to_path: _Path, progress: Optional[RemoteProgress] = ..., env: Optional[Any] = ..., multi_options: Optional[Any] = ..., **kwargs: Any) -> Repo: ...
    def archive(self, ostream: Any, treeish: Optional[Any] = ..., prefix: Optional[Any] = ..., **kwargs: Any) -> Any: ...
    def has_separate_working_tree(self) -> bool: ...
    rev_parse: Any = ...
    def currently_rebasing_on(self) -> Commit: ...
