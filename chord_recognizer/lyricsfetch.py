from dataclasses import dataclass
import syncedlyrics
import datetime
import vamp # type: ignore
import librosa
import os
import yt_dlp

def download_audio(query: str) -> str:
    filename = f"{query}.mp3"
    if os.path.exists(filename):
        return filename
    # Create a YoutubeDL object with the desired options
    ydl_opts = {
        # Use ytsearch: prefix to search for the query on YouTube
        "default_search": "ytsearch:",
        # Download only the audio track
        "format": "bestaudio",
        # Extract the audio and convert it to mp3
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        # Use the video title as the output filename
        #"outtmpl": "%(title)s.%(ext)s",
        "outtmpl": query,
    }
    # Create a YoutubeDL object with the options
    ydl = yt_dlp.YoutubeDL(ydl_opts)
    # Download the audio of the first result for the query
    ydl.download([query])
    return filename

def get_chords_for_song(path: str)-> list[dict[str, float | str]]:
    data, rate = librosa.load(path)
    chordino: dict = vamp.collect(data, rate, "nnls-chroma:chordino")
    return chordino["list"]

# Parse to class
@dataclass
class Lyric:
    start: float # time in seconds
    text: str	

def get_lyrics_for_song(title: str) -> list[Lyric]:
    # Check if we have lyrics in cache
    # If not, fetch from web
    if os.path.exists(title + ".lrc"):
        with open(title + ".lrc", "r", encoding="utf-8") as f:
            res = f.read()
    else:
        res = syncedlyrics.search(title)
        if res is None:
            raise Exception("No lyrics found")
        else:
            with open(title + ".lrc", "w") as f:
                f.write(res)
    
    lyrics: list[Lyric] = []
    for line in res.splitlines():
        if line.startswith("["):
            time, text = line.split("]", 1)
            time = time[1:]
            if time[0].isdigit() == False:
                continue
            time = datetime.datetime.strptime(time, "%M:%S.%f")
            time = time.minute * 60 + time.second + time.microsecond / 1000000
            lyrics.append(Lyric(time, text))

    print(lyrics)        

    return lyrics
    
def build_chord_sheet(lrc_lyrics: list[Lyric], chords: list[dict[str, float | str]]) -> str:
    print(chords)
    print(lrc_lyrics)
    # Iterate over lyrics
    chord_sheet = ""

    for i, lyric in enumerate(lrc_lyrics):

        # Check if next lyric line exists
        try:
            next_lyric_start = lrc_lyrics[i+1].start
        except:
            next_lyric_start = 9999999.0
        
        while len(chords) > 0 and float(chords[0]["timestamp"]) < next_lyric_start:
            chord = chords.pop(0)
            chord_sheet += f"{chord['label']} "
        chord_sheet += f"\n{lyric.text}\n"
    
    return chord_sheet

    
if __name__ == "__main__":
    #NAME = "Best Coast - Feeling OK"
    NAME = "Ада - Стразы (Кишки)"
    filename = download_audio(NAME)
    chords = get_chords_for_song(filename)
    try:
        lyrics = get_lyrics_for_song(NAME)
        sheet = build_chord_sheet(lyrics, chords)
        print(sheet)
    except:
        print(chords)
        
    quit()

    #chords = get_chords_for_song("Best Coast - In My Eyes-(p).opus")
    # Turn on logging
    #logging.basicConfig(level=logging.DEBUG)
    




    lyrics = get_lyrics_for_song("Best Coast In My Eyes")
    sheet = build_chord_sheet(lyrics, chords)
    print(sheet)