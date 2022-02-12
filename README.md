This repository holds a snapshot of Khaganate, a suite of productivity tools that I wrote for my own use.

The canonical Khaganate source code is kept in a private repository as it contains various secrets and non-public information. This repository is a snapshot as of February 2022, with private information scrubbed and certain hard-coded parameters changed. As it required a good deal of effort to scrub the source code, I do not intend to keep this repository up to date with the canonical repository.

The source code in this repository is released under the MIT license (see the accompanying LICENSE file), which means that you are free to do what you wish with the code as long as you preserve the copyright notice.

## Requirements
I run Khaganate with:

- Ubuntu 20.04
- Python 3.8
- npm 7.5

Other configurations are untested.

## Installation
First, you will need to clone the repository:

```shell
git clone https://github.com/iafisher/khaganate-snapshot.git
cd khaganate-snapshot
```

Next, create a virtual environment and install Python dependencies:

```shell
virtualenv --python=python3 .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

Install JavaScript dependencies and build the frontend:

```
npm install
npm run build
```

Run Django database migrations:

```
./manage.py migrate
```

Now, you are ready to run the server:

```
./manage.py runserver 8000
```

Sections below contain optional installation steps.

### Optional: Install browser extensions
Khaganate comes with two browser extensions: a go link extensions and a bookmarks extension.

The go links extension was described in [one of my earlier blog posts](https://iafisher.com/blog/2020/10/golinks). It allows you to create 'go links' in Khaganate which you can enter into your browser search bar as 'go/whatever'. It also supports a few other short links, such as 's/' to search Khaganate.

The bookmarks extension allows you to bookmark web pages in Khaganate's database. It supports more metadata than the built-in browser bookmarks manager and allows you to tag bookmarks with a hierarchical set of topics that you can browse within Khaganate.

To install these extensions in Chrome, enter chrome://extensions in your address bar, then click on "Load unpacked" and navigate to the `extensions/bookmarks` or `extensions/golinks` folder to install the extensions.

Note that these extensions expect the server to be running locally on port 8000. If you wish to run the server on a different port, you will need to edit the extension source code.

### Optional: Set up scripts
The `scripts/` directory contains a few useful scripts that you may wish to add to your `PATH`.

- `kg` runs the daily task and starts the server.
- `kgx` has a variety of management commands. Run `kgx --help` for details.
- `kgdb` is a wrapper around the [`isqlite`](https://github.com/iafisher/isqlite) CLI. It is used to query and manage the database. You will need to edit `scripts/kgdb` to set the path to the database.

### Optional: Set up search indexing
To set up search indexing, you will first need to run `scripts/rebuild_index`. Then, periodically (e.g., with a cron job) run `scripts/update_index` to update the index.

### Optional: Customize settings
`base/constants.py` contains customizable settings, mostly the locations of various things on the filesystem, which you may wish to change.

Note that if you change the location of the database, you will need to either copy the sample database in this repository at `files/me.sqlite3`, or else run `isqlite migrate path/to/database base/schema.py` to create the database schema.

### Optional: Create data
Many things in Khaganate can be created from the frontend, including calendar events, tasks, financial transactions, books, and films. Some less-frequently created objects have to be created on the command-line:

- Habits (`habits`)
- Goals (`goals`)
- Recurring calendar events (`calendar_recurring_events`)

You can create these objects interactively with `isqlite icreate <path to database> <table name>`. The table name is listed in parentheses above.
