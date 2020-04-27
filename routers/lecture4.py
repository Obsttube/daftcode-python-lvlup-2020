from fastapi import APIRouter, Response, status
from pydantic import BaseModel
import aiosqlite

router = APIRouter()

@router.on_event("startup")
async def startup():
	router.db_connection = await aiosqlite.connect('chinook.db')

@router.on_event("shutdown")
async def shutdown():
	await router.db_connection.close()

@router.get("/tracks")
async def tracks(page: int = 0, per_page: int = 10):
	router.db_connection.row_factory = aiosqlite.Row
	cursor = await router.db_connection.execute("SELECT * FROM tracks ORDER BY TrackId LIMIT :per_page OFFSET :per_page*:page",
		{'page': page, 'per_page': per_page})
	tracks = await cursor.fetchall()
	return tracks

@router.get("/tracks/composers")
async def tracks_composers(response: Response, composer_name: str):
	router.db_connection.row_factory = lambda cursor, x: x[0]
	cursor = await router.db_connection.execute("SELECT Name FROM tracks WHERE Composer = ? ORDER BY Name",
		(composer_name, ))
	tracks = await cursor.fetchall()
	if len(tracks) == 0:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Cannot find any songs of that composer."}}
	return tracks

class Album(BaseModel):
    title: str
    artist_id: int

@router.post("/albums")
async def add_album(response: Response, album: Album):
	router.db_connection.row_factory = None
	cursor = await router.db_connection.execute("SELECT ArtistId FROM artists WHERE ArtistId = ?",
		(album.artist_id, ))
	result = await cursor.fetchone()
	if result is None:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Artist with that ID does not exist."}}
	cursor = await router.db_connection.execute("INSERT INTO albums (Title, ArtistId) VALUES (?, ?)",
		(album.title, album.artist_id))
	await router.db_connection.commit()
	response.status_code = status.HTTP_201_CREATED
	return {"AlbumId": cursor.lastrowid, "Title": album.title, "ArtistId": album.artist_id}

@router.get("/albums/{album_id}")
async def tracks_composers(response: Response, album_id: int):
	router.db_connection.row_factory = aiosqlite.Row
	cursor = await router.db_connection.execute("SELECT * FROM albums WHERE AlbumId = ?",
		(album_id, ))
	album = await cursor.fetchall()
	#print(dict(album)) #{'AlbumId': 348, 'Title': 'Mandaryna HITS', 'ArtistId': 1}
	'''if album is None:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Album with that ID does not exist."}}'''
	response.status_code = status.HTTP_200_OK
	return album