import os


BOT_NAME = "covid19bahia"

SPIDER_MODULES = ["covid19bahia.spiders"]
NEWSPIDER_MODULE = "covid19bahia.spiders"

USER_AGENT = "covid19bahia (+http://www.dadosabertosdefeira.com.br)"

ROBOTSTXT_OBEY = True

if os.getenv("DEV_ENVIRONMENT"):
    HTTPCACHE_ENABLED = True
    HTTPCACHE_EXPIRATION_SECS = 8600

ITEM_PIPELINES = {
    "covid19bahia.pipelines.DatabaseWriterPipeline": 100,
}
