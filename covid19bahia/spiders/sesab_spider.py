from datetime import datetime
import scrapy


class NewsSpider(scrapy.Spider):
    name = "sesab_news"
    start_urls = ["http://www.saude.ba.gov.br/noticias"]

    def parse(self, response):
        titles = response.css("div.detalhes-noticias h2 ::text").extract()
        urls = response.css("div.detalhes-noticias h2 a::attr(href)").extract()
        dates = response.css("div.detalhes-noticias p.data-hora ::text").extract()

        continue_crawling = True
        for index, url in enumerate(urls):
            date_obj = datetime.strptime(dates[index], "%d/%m/%Y %H:%M")

            # essa abordagem assume que as notícias são sempre ordenadas
            if self.last_news_date is None or date_obj > self.last_news_date:
                news = {
                    "date": date_obj,
                    "url": urls[index],
                    "title": titles[index],
                    "crawled_at": datetime.now(),
                }
                yield response.follow(url, self.parse_page, meta={"news": news})
            else:
                continue_crawling = False
                break

        if continue_crawling:
            next_page_url = response.css("li a.next::attr(href)").extract_first()
            if next_page_url:
                yield scrapy.Request(next_page_url)

    def parse_page(self, response):
        news = response.meta["news"]
        key_words = ["covid19", "covid-19", "coronavirus", "coronavírus"]

        text = response.css("div#conteudo div.container p ::text").extract()
        text = " ".join(text)
        news["text"] = text
        for key_word in key_words:
            key_word_in_title = key_word in news["title"].lower()
            key_word_in_text = key_word in news["text"].lower()
            if key_word_in_title or key_word_in_text:
                yield news
                break
