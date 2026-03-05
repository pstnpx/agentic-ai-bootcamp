from typing import Any
from mcp.server import InitializationOptions
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.stdio import stdio_server
import mcp.types as types
from typing import List
import sqlite3
import json
from pathlib import Path

class QNA:
    def __init__(self,db_path):
        self.db_path = str(Path().resolve().joinpath(db_path))

    def _lookup_track(
        self,
        track_name: str | None = None,
        album_title: str | None = None,
        artist_name: str | None = None,
    ) -> List[types.TextContent]:
        """Lookup a track in Chinook DB based on identifying information about.

        Returns:
            a list of dictionaries per matching track that contain keys {'track_name', 'artist_name', 'album_name'}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
        SELECT DISTINCT t.Name as track_name, ar.Name as artist_name, al.Title as album_name
        FROM Track t
        JOIN Album al ON t.AlbumId = al.AlbumId
        JOIN Artist ar ON al.ArtistId = ar.ArtistId
        WHERE 1=1
        """
        params = []

        if track_name:
            # track_name = track_store.similarity_search(track_name, k=1)[0].page_content
            query += " AND t.Name LIKE ?"
            params.append(f"%{track_name}%")
        if album_title:
            # album_title = album_store.similarity_search(album_title, k=1)[0].page_content
            query += " AND al.Title LIKE ?"
            params.append(f"%{album_title}%")
        if artist_name:
            # artist_name = artist_store.similarity_search(artist_name, k=1)[0].page_content
            query += " AND ar.Name LIKE ?"
            params.append(f"%{artist_name}%")

        cursor.execute(query, params)
        results = cursor.fetchall()

        tracks = [
            {"track_name": row[0], "artist_name": row[1], "album_name": row[2]}
            for row in results
        ]

        conn.close()
        return [types.TextContent(
            type="text",
            text=json.dumps(tracks)
        )]

    def _lookup_album(
        self,
        track_name: str | None = None,
        album_title: str | None = None,
        artist_name: str | None = None,
    ) -> List[types.TextContent]:
        """Lookup an album in Chinook DB based on identifying information about.

        Returns:
            a list of dictionaries per matching album that contain keys {'album_name', 'artist_name'}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
        SELECT DISTINCT al.Title as album_name, ar.Name as artist_name
        FROM Album al
        JOIN Artist ar ON al.ArtistId = ar.ArtistId
        LEFT JOIN Track t ON t.AlbumId = al.AlbumId
        WHERE 1=1
        """
        params = []

        if track_name:
            query += " AND t.Name LIKE ?"
            params.append(f"%{track_name}%")
        if album_title:
            query += " AND al.Title LIKE ?"
            params.append(f"%{album_title}%")
        if artist_name:
            query += " AND ar.Name LIKE ?"
            params.append(f"%{artist_name}%")

        cursor.execute(query, params)
        results = cursor.fetchall()

        albums = [{"album_name": row[0], "artist_name": row[1]} for row in results]

        conn.close()
        return [types.TextContent(
            type="text",
            text=json.dumps(albums)
        )]

    def _lookup_artist(
        self,
        track_name: str | None = None,
        album_title: str | None = None,
        artist_name: str | None = None,
    ) -> List[types.TextContent]:
        """Lookup an album in Chinook DB based on identifying information about.

        Returns:
            a list of matching artist names
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
        SELECT DISTINCT ar.Name as artist_name
        FROM Artist ar
        LEFT JOIN Album al ON al.ArtistId = ar.ArtistId
        LEFT JOIN Track t ON t.AlbumId = al.AlbumId
        WHERE 1=1
        """
        params = []

        if track_name:
            query += " AND t.Name LIKE ?"
            params.append(f"%{track_name}%")
        if album_title:
            query += " AND al.Title LIKE ?"
            params.append(f"%{album_title}%")
        if artist_name:
            query += " AND ar.Name LIKE ?"
            params.append(f"%{artist_name}%")

        cursor.execute(query, params)
        results = cursor.fetchall()

        artists = [row[0] for row in results]

        conn.close()
        return [types.TextContent(
            type="text",
            text=json.dumps(artists)
        )]

async def main(db_path:str):
    qna = QNA(db_path)
    mcp = Server("qna")
    @mcp.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="lookup_track",
                description="Lookup a track in Chinook DB",
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "track_name": {"type": "string", "description": "Track name"},
                        "album_title": {"type": "string", "description": "Album title"},
                        "artist_name": {"type": "string", "description": "Artist name"},
                    }, 
                    "required": []},
            ),
            types.Tool(
                name="lookup_album",
                description="Lookup an album in Chinook DB",
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "track_name": {"type": "string", "description": "Track name"},
                        "album_title": {"type": "string", "description": "Album title"},
                        "artist_name": {"type": "string", "description": "Artist name"},
                    }, 
                    "required": []},
            ),
            types.Tool(
                name="lookup_artist",
                description="Lookup an artist in Chinook DB",
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "track_name": {"type": "string", "description": "Track name"},
                        "album_title": {"type": "string", "description": "Album title"},
                        "artist_name": {"type": "string", "description": "Artist name"},
                    }, 
                    "required": []},            
            )
        ]

    @mcp.call_tool()
    async def handle_call_tool(name: str, args: dict[str, Any] | None):
        input_keys = { "track_name", "album_title", "artist_name"}
        # Empty args
        if args is None or args == {}:
            raise ValueError("args cannot be None")
        # Invalid keys
        invalid_keys = set(args.keys()) - input_keys
        if invalid_keys:
            raise ValueError(f"Invalid keys in args: {invalid_keys}")
        # Empty values
        empty_keys = [k for k, v in args.items() if v is None or v == ""]
        if empty_keys:
            raise ValueError(f"Empty values for keys: {empty_keys}")
        
        try :
            if name == "lookup_track":
                return qna._lookup_track(**args)
            elif name == "lookup_album":
                return qna._lookup_album(**args)
            elif name == "lookup_artist":
                return qna._lookup_artist(**args)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
        ## TODO
        ## implement tool calling logic
        pass
    
    async with stdio_server() as (read_stream,write_stream):
        await mcp.run(read_stream, write_stream, InitializationOptions(
                server_name="qna",
                server_version="0.1.0",
                capabilities=mcp.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),raise_exceptions=True)

class ServerWrapper():
    """A wrapper to compat with mcp[cli]"""
    def run(self):
        import asyncio
        asyncio.run(main())

wrapper = ServerWrapper()