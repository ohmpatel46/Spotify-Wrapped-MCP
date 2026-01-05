from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Mapping, Sequence


class BaseProvider(ABC):
    @abstractmethod
    def get_me(self) -> Mapping[str, object]:
        raise NotImplementedError

    @abstractmethod
    def get_top_tracks(self, time_range: str, limit: int) -> Mapping[str, object]:
        raise NotImplementedError

    @abstractmethod
    def get_top_artists(self, time_range: str, limit: int) -> Mapping[str, object]:
        raise NotImplementedError

    @abstractmethod
    def get_recently_played(self, limit: int) -> Mapping[str, object]:
        raise NotImplementedError

    @abstractmethod
    def get_tracks(self, ids: Sequence[str]) -> Mapping[str, object]:
        raise NotImplementedError

    @abstractmethod
    def get_artists(self, ids: Sequence[str]) -> Mapping[str, object]:
        raise NotImplementedError

    @abstractmethod
    def create_playlist(
        self, user_id: str, name: str, public: bool, description: str
    ) -> Mapping[str, object]:
        raise NotImplementedError

    @abstractmethod
    def add_tracks(self, playlist_id: str, uris: Iterable[str]) -> Mapping[str, object]:
        raise NotImplementedError
