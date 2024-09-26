DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    quantity INTEGER DEFAULT 0,
    image_url TEXT
);

CREATE TABLE recent_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    pfp_path TEXT DEFAULT 'uploads/placeholder.png' -- Store PFP path directly here
);

CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pfp_path TEXT DEFAULT 'uploads/placeholder.png',
    -- Add other settings fields as needed
    FOREIGN KEY (user_id) REFERENCES users(id) -- Assuming you have a users table
);
