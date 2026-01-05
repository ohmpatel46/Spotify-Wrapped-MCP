# Spotify Wrapped MCP (Mock)

This repo provides a local, end-to-end Spotify Wrapped-style MCP server using a fake Spotify API.
The provider interface is designed so you can swap in a real Spotify Web API provider later.

## Setup

- `conda activate spotify-mcp`
- `pip install -r requirements.txt`
  - or: `conda env update -f environment.yml`

## Run the fake API

- `uvicorn fake_spotify_api.api:app --port 7777 --reload`

## Run the MCP server

- `python -m mcp_server.server`

## Environment

Create a `.env` from `.env.example` if you want to override defaults.

```
MODE=mock
SPOTIFY_BASE_URL=http://localhost:7777/v1
```

## MCP tools

- `wrapped_summary(time_range="short_term")`
- `create_wrapped_playlist(time_range="short_term", public=false)`

