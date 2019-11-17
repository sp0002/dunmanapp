CREATE TABLE user (
  id TEXT PRIMARY KEY,
  classid TEXT NOT NULL,
  name TEXT,
  email TEXT UNIQUE NOT NULL,
  profile_pic TEXT NOT NULL,
  admin INTEGER NOT NULL
);

