# uTRILib

\[micro\] Track Info Library is a tool helping you to download & preserver your Spotify library locally.

# Legal notice
This tool is provided for personal, non-commercial use only. In Russia, personal copying of lawfully obtained sound recordings is permitted under [Article 1273 of the Civil Code](https://www.consultant.ru/document/cons_doc_LAW_64629/f63562ebf49f4d5fbe0c3daa9ea22a689d2d64ab/). In the United States, the [Audio Home Recording Act](https://www.congress.gov/bill/102nd-congress/senate-bill/1623) allows private copying of legally obtained music, but other laws (including the DMCA) prohibit bypassing DRM or downloading copyrighted content without authorization. You are solely responsible for ensuring your use complies with local laws.

# Usage

1. Clone this repo somewhere
2. Install Python 3.11
3. `pip install -r requirements.txt` 
4. Install & run [TRILib-Spotify](https://github.com/VastieOfficial/TRILIB-Spotify)
5. Set enviveroment variables:

| Variable         | Value                                                     
| ---------------: | --------------------------------------------------------- 
| TRI_CACHE        | Path to Trilib's cache (any folder, default CWD/TRICACHE) 
| TRI_SPOTIFY_PORT | HTTP port (default 3500)                                  
6. Authorize with the script:
`python api.py`
7. Save your data with [spotmybackup.com](https://spotmybackup.com) to `backup.json`
8. `python parse.py` to parse all the tracks info
9. `python download.py` to download the tracks
10. `python rebuildM3U8.py` to rebuild your playlists with the TRILIB cache
11. Done. You will need to rebuild M3U8 files if you move the cache TRILIB cache folder. Other than that, you can move them whereever you want on current PC.

# License
This software is released under MIT license. 
