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
                    date text,
                    url text,
                    title text,
                    crawled_at,
                    text text
                );
            """
            )

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        self.cursor.execute(
            f"""
            INSERT INTO news
            VALUES (
                \'{item['date']}\', \'{item['url']}\', 
                \'{item['title']}\', \'{item['crawled_at']}\', \'{item['text']}\');
        """
        )
        self.db.commit()
        return item
