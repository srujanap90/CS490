-- Initialize the database.
-- Drop any existing data and create empty tables.

-- initialize old data. we dont drop user after initialized
-- DROP TABLE IF EXISTS user; 
-- DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS comments;

-- CREATE TABLE user (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   username TEXT UNIQUE NOT NULL,
--   password TEXT NOT NULL,
--   useremail TEXT UNIQUE NOT NULL
-- );

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  img_url TEXT DEFAULT NONE,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
CREATE TABLE comments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  body TEXT NOT NULL,
  post_id INTEGER NOT NULL,
  retweet_id INTEGER NOT NULL DEFAULT 0
  -- FOREIGN KEY (author_id) REFERENCES user (id)
  -- FOREIGN KEY (post_id) REFERENCES post (id)
);
