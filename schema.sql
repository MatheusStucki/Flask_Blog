DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    quantity INTEGER DEFAULT 0,
    image_url TEXT,
    max_quantity INTEGER DEFAULT 0,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE recent_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_name VARCHAR(255) NOT NULL UNIQUE,
    pfp_path TEXT DEFAULT 'uploads/placeholder.jpeg'
);

