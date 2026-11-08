CREATE TABLE IF NOT EXISTS gigs(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 title TEXT NOT NULL,
 description TEXT NOT NULL,
 category TEXT NOT NULL,
 price INTEGER NOT NULL CHECK(price > 0),
 payment_method TEXT NOT NULL,
 seller_name TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'pending',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS gigs_status_idx ON gigs(status);
CREATE INDEX IF NOT EXISTS gigs_category_idx ON gigs(category);
