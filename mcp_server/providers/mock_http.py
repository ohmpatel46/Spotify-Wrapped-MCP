from __future__ import annotations

from typing import Iterable, Mapping, Sequence

import httpx

from .base import BaseProvider


class MockHttpProvider(BaseProvider):
    def __init__(self, base_url: str) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=10.0)

    def _get(self, path: str, params: Mapping[str, object] | None = None) -> Mapping[str, object]:
        try:
            response = self._client.get(path, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Mock API GET {path} failed: {exc}") from exc
        return response.json()

    def _post(self, path: str, payload: Mapping[str, object]) -> Mapping[str, object]:
        try:
            response = self._client.post(path, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Mock API POST {path} failed: {exc}") from exc
        return response.json()

    def get_me(self) -> Mapping[str, object]:
        return self._get("/me")

    def get_top_tracks(self, time_range: str, limit: int) -> Mapping[str, object]:
        return self._get("/me/top/tracks", params={"time_range": time_range, "limit": limit})

    def get_top_artists(self, time_range: str, limit: int) -> Mapping[str, object]:
        return self._get("/me/top/artists", params={"time_range": time_range, "limit": limit})

    def get_recently_played(self, limit: int) -> Mapping[str, object]:
        return self._get("/me/player/recently-played", params={"limit": limit})

    def get_tracks(self, ids: Sequence[str]) -> Mapping[str, object]:
        if not ids:
            return {"tracks": []}
        return self._get("/tracks", params={"ids": ",".join(ids)})

    def get_artists(self, ids: Sequence[str]) -> Mapping[str, object]:
        if not ids:
            return {"artists": []}
        return self._get("/artists", params={"ids": ",".join(ids)})

    def create_playlist(
        self, user_id: str, name: str, public: bool, description: str
    ) -> Mapping[str, object]:
        payload = {"name": name, "public": public, "description": description}
        return self._post(f"/users/{user_id}/playlists", payload)

    def add_tracks(self, playlist_id: str, uris: Iterable[str]) -> Mapping[str, object]:
        payload = {"uris": list(uris)}
        return self._post(f"/playlists/{playlist_id}/tracks", payload)
