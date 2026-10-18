-- Ribbit Platform SQLite Database Schema (English, Normalized DDL)

CREATE TABLE IF NOT EXISTS plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    monthly_price REAL NOT NULL,
    max_profiles INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    spotify_id TEXT UNIQUE,
    display_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    plan_id INTEGER NOT NULL REFERENCES plans(plan_id),
    primary_account_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    blocked_genres TEXT,
    is_admin INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE TABLE IF NOT EXISTS tracks (
    track_id INTEGER PRIMARY KEY AUTOINCREMENT,
    spotify_id TEXT,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    album TEXT,
    duration_seconds INTEGER NOT NULL,
    genre TEXT NOT NULL,
    country TEXT,
    release_year INTEGER,
    cover_url TEXT,
    itunes_preview_url TEXT,
    explicit INTEGER NOT NULL DEFAULT 0,
    is_deleted INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tracks_title ON tracks(title);
CREATE INDEX IF NOT EXISTS idx_tracks_artist ON tracks(artist);
CREATE INDEX IF NOT EXISTS idx_tracks_genre ON tracks(genre);

CREATE TABLE IF NOT EXISTS interactions (
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL REFERENCES tracks(track_id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    created_at TEXT NOT NULL,
    CONSTRAINT uq_interactions_user_track UNIQUE (user_id, track_id)
);

CREATE TABLE IF NOT EXISTS playlists (
    playlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    spotify_playlist_id TEXT,
    is_exported INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS playlist_tracks (
    playlist_track_id INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_id INTEGER NOT NULL REFERENCES playlists(playlist_id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL REFERENCES tracks(track_id) ON DELETE CASCADE,
    added_at TEXT NOT NULL,
    CONSTRAINT uq_playlist_tracks_playlist_track UNIQUE (playlist_id, track_id)
);

CREATE TABLE IF NOT EXISTS jams (
    jam_id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    room_name TEXT NOT NULL,
    room_code TEXT NOT NULL UNIQUE,
    is_active INTEGER NOT NULL DEFAULT 1,
    current_track_id INTEGER REFERENCES tracks(track_id) ON DELETE SET NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jam_queue_items (
    jam_queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    jam_id INTEGER NOT NULL REFERENCES jams(jam_id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL REFERENCES tracks(track_id) ON DELETE CASCADE,
    vote_points INTEGER NOT NULL DEFAULT 0,
    added_at TEXT NOT NULL,
    CONSTRAINT uq_jam_queue_items_jam_track UNIQUE (jam_id, track_id)
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL REFERENCES tracks(track_id) ON DELETE CASCADE,
    rating INTEGER NOT NULL,
    text TEXT,
    likes_count INTEGER NOT NULL DEFAULT 0,
    is_deleted INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_reviews_track_id ON reviews(track_id);
