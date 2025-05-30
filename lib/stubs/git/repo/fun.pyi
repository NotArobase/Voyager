from typing import Any, Optional

Repo = Any #from . import Repo
from ..objects.base import Object
from ..objects.tag import TagObject
from ..objects.commit import Commit
from ..db import GitCmdObjectDB

def touch(filename: str) -> str: ...
def is_git_dir(d: str) -> bool: ...
def find_worktree_git_dir(dotgit: str) -> Optional[str]: ...
def find_submodule_git_dir(d: str) -> Optional[str]: ...
def short_to_long(odb: GitCmdObjectDB, hexsha: bytes) -> bytes: ...
def name_to_object(repo: Repo, name: str, return_ref: bool = ...) -> Object: ...
def deref_tag(tag: TagObject) -> Object: ...
def to_commit(obj: Object) -> Commit: ...
def rev_parse(repo: Repo, rev: str) -> Object: ...
