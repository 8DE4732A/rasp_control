CREATE TABLE IF NOT EXISTS "vmess" (
	"id"	INTEGER NOT NULL UNIQUE,
    "name"  TEXT,
	"vmess"	TEXT,
	"used"	INTEGER DEFAULT 0,
    "ookla" TEXT,
	PRIMARY KEY("id")
) 