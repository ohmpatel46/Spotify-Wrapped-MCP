from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Iterable, Mapping


def _top_name_id(items: Iterable[Mapping[str, object]], limit: int) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for item in items:
        item_id = str(item.get("id", ""))
        name = str(item.get("name", ""))
        if item_id and name:
            result.append({"id": item_id, "name": name})
        if len(result) >= limit:
            break
    return result


def _genre_dna(artists: Iterable[Mapping[str, object]], limit: int) -> list[str]:
    counter: Counter[str] = Counter()
    for artist in artists:
        for genre in artist.get("genres", []) or []:
            counter[str(genre)] += 1
    return [genre for genre, _count in counter.most_common(limit)]


def _mainstream_vs_niche(tracks: Iterable[Mapping[str, object]]) -> dict[str, object]:
    popularities = [int(track.get("popularity", 0)) for track in tracks if "popularity" in track]
    avg_popularity = round(sum(popularities) / len(popularities), 2) if popularities else 0.0
    if avg_popularity >= 70:
        label = "Mainstream"
    elif avg_popularity >= 40:
        label = "Balanced"
    else:
        label = "Deep Cuts"
    return {"average_popularity": avg_popularity, "label": label}


def _time_of_day_vibe(recently_played: Mapping[str, object]) -> str:
    items = recently_played.get("items", []) or []
    if len(items) < 5:
        return "insufficient_data"

    buckets = Counter()
    for entry in items:
        played_at = entry.get("played_at")
        if not played_at:
            continue
        try:
            dt = datetime.fromisoformat(str(played_at).replace("Z", "+00:00"))
        except ValueError:
            continue
        hour = dt.hour
        if 5 <= hour <= 11:
            buckets["morning"] += 1
        elif 12 <= hour <= 17:
            buckets["afternoon"] += 1
        elif 18 <= hour <= 22:
            buckets["evening"] += 1
        else:
            buckets["late_night"] += 1

    if not buckets:
        return "insufficient_data"

    return buckets.most_common(1)[0][0]


def _headline(top_artist: str | None, top_track: str | None, vibe_label: str, time_vibe: str) -> str:
    artist_text = top_artist or "Unknown artist"
    track_text = top_track or "Unknown track"
    suffix = ""
    if time_vibe != "insufficient_data":
        suffix = f", especially in the {time_vibe.replace('_', ' ')}"
    return f"Top artist {artist_text} and top track {track_text} give a {vibe_label.lower()} vibe{suffix}."


def wrapped_summary(provider, time_range: str = "short_term") -> dict[str, object]:
    top_tracks_payload = provider.get_top_tracks(time_range=time_range, limit=20)
    top_artists_payload = provider.get_top_artists(time_range=time_range, limit=20)
    recently_played = provider.get_recently_played(limit=20)

    top_tracks_items = top_tracks_payload.get("items", []) or []
    top_artists_items = top_artists_payload.get("items", []) or []

    top_tracks = _top_name_id(top_tracks_items, 5)
    top_artists = _top_name_id(top_artists_items, 5)

    genre_dna = _genre_dna(top_artists_items, 5)
    mainstream_vs_niche = _mainstream_vs_niche(top_tracks_items)
    time_vibe = _time_of_day_vibe(recently_played)

    headline = _headline(
        top_artists[0]["name"] if top_artists else None,
        top_tracks[0]["name"] if top_tracks else None,
        mainstream_vs_niche["label"],
        time_vibe,
    )

    return {
        "headline": headline,
        "top_artists": top_artists,
        "top_tracks": top_tracks,
        "genre_dna": genre_dna,
        "mainstream_vs_niche": mainstream_vs_niche,
        "time_of_day_vibe": time_vibe,
    }


def create_wrapped_playlist(provider, time_range: str = "short_term", public: bool = False) -> dict[str, object]:
    user = provider.get_me()
    user_id = str(user.get("id", "mock_user"))

    top_tracks_payload = provider.get_top_tracks(time_range=time_range, limit=20)
    top_tracks_items = top_tracks_payload.get("items", []) or []
    track_uris = [track.get("uri") for track in top_tracks_items if track.get("uri")]

    name = f"Wrapped ({time_range})"
    description = f"Your top tracks for {time_range}."
    playlist = provider.create_playlist(user_id=user_id, name=name, public=public, description=description)
    playlist_id = str(playlist.get("id", ""))

    if track_uris and playlist_id:
        provider.add_tracks(playlist_id=playlist_id, uris=track_uris)

    return {
        "playlist_id": playlist_id,
        "playlist_url": playlist.get("external_urls", {}).get("spotify", ""),
    }
