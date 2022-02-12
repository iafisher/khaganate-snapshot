"""
Basic constants for Khaganate, mostly locations of various things on the filesystem.
"""
import os

BASE = os.path.dirname(os.path.dirname(__file__))

# The main files directory.
FILES = os.path.join(BASE, "files")

# The folder containing server and cron job logs.
LOGS_FOLDER = os.path.join(FILES, ".logs")

# The folder containing the search index.
SEARCH_INDEX = os.path.join(FILES, ".index")

# The path to the database.
DATABASE_PATH = os.path.join(FILES, "me.sqlite3")

# The preferred text editor program.
EDITOR = "vim"

# The preferred browser program.
BROWSER = "google-chrome"
