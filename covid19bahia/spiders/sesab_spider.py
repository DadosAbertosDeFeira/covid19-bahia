import scrapy


class NewsSpider(scrapy.Spider):
    name = "sesab_news"
    start_urls = ["http://www.saude.ba.gov.br/noticias"]

    def parse(self, response):
        titles = response.css('div.detalhes-noticias h2 ::text').extract()
        urls = response.css('div.detalhes-noticias h2 a::attr(href)').extract()
        published_at = response.css('div.detalhes-noticias p.data-hora ::text').extract()
        categories = response.css('div.detalhes-noticias p.categoria a::text').extract()
        categories_url = response.css('div.detalhes-noticias p.categoria a::attr(href)').extract()

        for index, url in enumerate(urls):
            news = {
                "title": titles[index],
                "url": urls[index],
                "published_at": published_at[index],
                "category": categories[index],
                "category_url": categories_url[index],
            }
            yield response.follow(url, self.parse_page, meta={"news": news})

        next_page_url = response.css('li a.next::attr(href)').extract_first()
        if next_page_url:
            yield scrapy.Request(next_page_url)

    def parse_page(self, response):
        news = response.meta["news"]
        key_words = ["covid19", "covid-19", "coronavirus"]

        text = response.css('div#conteudo div.container p ::text').extract()
        text = ' '.join(text)
        news["text"] = text
        for key_word in key_words:
            if key_word in news["title"].lower():
                yield news
                break
