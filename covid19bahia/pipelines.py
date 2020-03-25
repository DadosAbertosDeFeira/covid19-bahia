import sqlite3


class DatabaseWriterPipeline(object):
    def open_spider(self, spider):
        self.db = sqlite3.connect("sesab-news.db")
        self.cursor = self.db.cursor()

        table_exists = self.cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='news';
        """
        ).fetchone()

        if not table_exists:
            self.cursor.execute(
                """CREATE TABLE news
                (
                    date TEXT,
                    url TEXT,
                    title TEXT,
                    crawled_at TEXT,
                    text TEXT,
                    is_synced INTEGER
                );
            """
            )

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        self.save_item(item)
        return item

    def save_item(self, item):
        self.cursor.execute("SELECT * FROM news WHERE url=?", (item["url"],))
        found = self.cursor.fetchone()
        if not found:
            self.cursor.execute(
                f"""
                INSERT INTO news
                VALUES (
                    \'{item['date']}\',
                    \'{item['url']}\',
                    \'{item['title']}\',
                    \'{item['crawled_at']}\',
                    \'{item['text']}\',
                    0
                );
            """
            )
        self.db.commit()
