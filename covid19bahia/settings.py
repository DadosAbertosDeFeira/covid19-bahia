import os


BOT_NAME = "covid19bahia"

SPIDER_MODULES = ["covid19bahia.spiders"]
NEWSPIDER_MODULE = "covid19bahia.spiders"

USER_AGENT = "covid19bahia (+http://www.dadosabertosdefeira.com.br)"

ROBOTSTXT_OBEY = True

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 8600 if os.getenv("DEV_ENVIRONMENT") else None

ITEM_PIPELINES = {
    "covid19bahia.pipelines.DatabaseWriterPipeline": 100,
}
