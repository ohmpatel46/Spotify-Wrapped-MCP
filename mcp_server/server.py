from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from .providers.mock_http import MockHttpProvider
from .wrapped import create_wrapped_playlist, wrapped_summary


def _get_provider():
    mode = os.getenv("MODE", "mock").lower()
    if mode != "mock":
        raise RuntimeError(f"Unsupported MODE: {mode}")
    base_url = os.getenv("SPOTIFY_BASE_URL", "http://localhost:7777/v1")
    return MockHttpProvider(base_url=base_url)


_provider = _get_provider()

mcp = FastMCP("spotify-wrapped-mcp")


@mcp.tool()
def wrapped_summary(time_range: str = "short_term") -> dict:
    """Generate wrapped summary cards."""
    return wrapped_summary(_provider, time_range=time_range)


@mcp.tool()
def create_wrapped_playlist(time_range: str = "short_term", public: bool = False) -> dict:
    """Create a playlist from top tracks."""
    return create_wrapped_playlist(_provider, time_range=time_range, public=public)


if __name__ == "__main__":
    mcp.run()

