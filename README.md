# COVID19-Bahia

Um crawler para ajudar na coleta de boletins e casos de COVID19 na Bahia.
Atualmente a SESAB (Secretaria de Saúde da Bahia) publica boletins e casos
na seção de notícias do seu site: http://www.saude.ba.gov.br/noticias/.

A ideia é coletar notícias que aparentam ser boletins ou casos e fazer a triagem
de maneira colaborativa com o [Brasil.IO](https://brasil.io/dataset/covid19).
Veja a _issue_ [aqui](https://github.com/turicas/covid19-br/issues/9).

### Executando local

Para executar o crawler, utilize:

```
scrapy crawl sesab_news
```

Para exportar os resultados para um CSV:

```
scrapy crawl sesab_news -o noticias-sesab.csv
```

Os itens coletados serão salvos em um banco Postgres.

Você deve criar um banco chamado `sesab`. Para habilitar
a conexão com o banco, configure uma variável de ambiente
chamada `DATABASE_URL`.

Para habilitar um cache de 24 horas e evitar muitos acessos ao site,
crie configure a variável de ambiente `DEV_ENVIRONMENT=True`.

Veja um exemplo de configuração no `.env.sample`.
