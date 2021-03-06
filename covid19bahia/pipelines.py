import json
import logging
import os
import sqlite3
from datetime import datetime

import gspread
import psycopg2
from oauth2client.service_account import ServiceAccountCredentials


logger = logging.getLogger(__name__)


class DatabaseWriterPipeline(object):
    def open_spider(self, spider):
        self.connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.cursor = self.connection.cursor()

        self.cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'news'
            );
        """
        )
        table_exists = self.cursor.fetchone()[0]
        spider.last_news_date = None

        if not table_exists:
            self.cursor.execute(
                """CREATE TABLE news
                (
                    id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    date TIMESTAMP NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    crawled_at TIMESTAMP NOT NULL,
                    text TEXT NOT NULL,
                    is_synced BOOLEAN NOT NULL
                );
            """
            )
            self.connection.commit()
        else:
            self.cursor.execute(
                """
                SELECT date FROM news ORDER BY date DESC LIMIT 1;
            """
            )
            date_obj = self.cursor.fetchone()
            if date_obj:
                spider.last_news_date = date_obj[0]

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        self.save_item(item)
        return item

    def save_item(self, item):
        self.cursor.execute("SELECT id FROM news WHERE url=%s", (item["url"],))
        found = self.cursor.fetchone()

        if not found:
            self.cursor.execute(
                """
                    INSERT INTO news (
                        date,
                        url,
                        title,
                        crawled_at,
                        text,
                        is_synced
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        FALSE
                    );
                """,
                (
                    item["date"],
                    item["url"],
                    item["title"],
                    item["crawled_at"],
                    item["text"],
                ),
            )
            self.connection.commit()


class SyncItemsToGoogleSheetsPipeline(object):
    def __init__(self, *args, **kwargs):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        keyfile_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            keyfile_dict, scope
        )

        gc = gspread.authorize(credentials)
        self.news_sheet = gc.open_by_key(os.getenv("GOOGLE_SHEET_ID")).sheet1

        super().__init__(*args, **kwargs)

    def close_spider(self, spider):
        connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, date, url, title, crawled_at, text
            FROM news WHERE is_synced=false ORDER BY date;
        """
        )
        not_synced_news = cursor.fetchall()

        for not_synced in not_synced_news:
            _id = not_synced[0]
            date = not_synced[1].strftime("%Y-%m-%d")  # formato do brasil.io
            url = not_synced[2]
            title = not_synced[3]
            crawled_at = str(not_synced[4])
            text = not_synced[5]

            try:
                # False significa 'não verificado'
                result = self.news_sheet.append_row(
                    [date, url, title, crawled_at, text, False]
                )
                if result["updates"]["updatedRows"] > 0:
                    cursor.execute(
                        """
                        UPDATE news SET is_synced = true WHERE id = %s;
                    """,
                        (_id,),
                    )
                    connection.commit()
                else:
                    logger.warning("Não pôde atualizar o banco: %s", result)
            except Exception as e:
                logger.error("Não pôde sincronizar: %s %s", e, result)
