from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Fake Spotify API")

BASE_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = BASE_DIR / "fixtures"


def _load_fixture(filename: str) -> dict:
    path = FIXTURES_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=500, detail=f"Missing fixture: {filename}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _filter_by_ids(items: list[dict], ids_param: str) -> list[dict | None]:
    ids = [item.strip() for item in ids_param.split(",") if item.strip()]
    if not ids:
        raise HTTPException(status_code=400, detail="ids query parameter is required")
    by_id = {item.get("id"): item for item in items}
    return [by_id.get(item_id) for item_id in ids]


@app.get("/v1/me")
def me() -> dict:
    return {"id": "mock_user_123", "display_name": "Mock User"}


@app.get("/v1/me/top/tracks")
def top_tracks(time_range: str = "short_term", limit: int = 20, offset: int = 0) -> dict:
    payload = _load_fixture("top_tracks_short.json")
    items = payload.get("items", [])
    payload["items"] = items[offset : offset + limit]
    payload["limit"] = limit
    payload["offset"] = offset
    return payload


@app.get("/v1/me/top/artists")
def top_artists(time_range: str = "short_term", limit: int = 20, offset: int = 0) -> dict:
    payload = _load_fixture("top_artists_short.json")
    items = payload.get("items", [])
    payload["items"] = items[offset : offset + limit]
    payload["limit"] = limit
    payload["offset"] = offset
    return payload


@app.get("/v1/me/player/recently-played")
def recently_played(limit: int = 20, after: int | None = None, before: int | None = None) -> dict:
    payload = _load_fixture("recently_played.json")
    items = payload.get("items", [])
    payload["items"] = items[:limit]
    payload["limit"] = limit
    if after is not None:
        payload["cursors"] = {"after": str(after)}
    if before is not None:
        payload["cursors"] = {"before": str(before)}
    return payload


@app.get("/v1/tracks")
def tracks(ids: str = Query(...)) -> dict:
    payload = _load_fixture("tracks_details.json")
    items = payload.get("tracks", [])
    return {"tracks": _filter_by_ids(items, ids)}


@app.get("/v1/artists")
def artists(ids: str = Query(...)) -> dict:
    payload = _load_fixture("artists_details.json")
    items = payload.get("artists", [])
    return {"artists": _filter_by_ids(items, ids)}


@app.post("/v1/users/{user_id}/playlists")
def create_playlist(user_id: str, body: dict) -> dict:
    playlist_id = f"mock_playlist_{uuid4().hex[:8]}"
    return {
        "id": playlist_id,
        "name": body.get("name", "Wrapped"),
        "public": body.get("public", False),
        "description": body.get("description", ""),
        "owner": {"id": user_id},
        "snapshot_id": f"snapshot_{uuid4().hex[:8]}",
        "external_urls": {"spotify": f"https://open.spotify.com/playlist/{playlist_id}"},
        "href": f"http://localhost:7777/v1/playlists/{playlist_id}",
        "type": "playlist",
        "uri": f"spotify:playlist:{playlist_id}",
        "tracks": {"href": f"http://localhost:7777/v1/playlists/{playlist_id}/tracks", "total": 0},
    }


@app.post("/v1/playlists/{playlist_id}/tracks")
def add_tracks(playlist_id: str, body: dict) -> dict:
    if not body.get("uris"):
        raise HTTPException(status_code=400, detail="uris list is required")
    return {"snapshot_id": f"snapshot_{uuid4().hex[:8]}"}
