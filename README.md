
Consumir uma API todas as vezes que precisamos buscar aeroportos estava ficando muito moroso e consumindo muitos recursos.

Precisamos fazer cache dos aeroportos em nosso banco de dados. Como a lista de aeroportos é dinâmica, precisamos atualizar diariamente esta base.

O desafio é criar um serviço/comando/CLI que permita processar diariamente a Domestic Airports API, inserindo e atualizando registros.

Basic Auth Login: demo Senha: swnvlD

Dica: Se você utilizar Django Framework, poderá fazer algo como... python manage.py import_airports
Importante:

Utilize o Banco de Dados de sua preferência. SQLite, Postgres, Mysql, MongoDB...
A modelagem do banco de dados fica a seu critério e será avaliada.
Dica: Utilizar SQLite pode reduzir o tempo de configuração


## Descrição da solução

Este projeto implementa um pequeno serviço em Django para consumir uma API externa de aeroportos e manter uma cópia (cache) local no banco de dados. A ideia é sincronizar os dados externamente e expô-los através de endpoints HTTP para leitura.

## Principais componentes
- `core.models.airport_model.Airport`: modela os aeroportos (iata, cidade, estado, latitude, longitude, timestamps).
- `core.models.import_log_model.ImportLogModel`: registra cada execução de import (inicio/fim, status, quantos registros criados/atualizados e detalhes).
- `core.services.import_airports_from_api`: lógica principal que faz a chamada à API externa (com Basic Auth quando necessário), atualiza/cria registros e persiste um `ImportLogModel` com o resultado.
- `core.management.commands.import_airports`: comando Django (`python manage.py import_airports`) que executa a função de import e escreve o resumo no stdout.
- `core.views.airport_views`: endpoints HTTP para listar aeroportos (`GET /airports/`), obter detalhe (`GET /airports/<iata>/`) e disparar um import por POST (`POST /airports/import/`).

## Endpoints
- GET /airports/ — lista todos os aeroportos cadastrados no banco.
- GET /airports/<iata>/ — retorna detalhes de um aeroporto (iata, cidade, estado, lat, lon).
- POST /airports/import/ — aciona manualmente o processo de import. Aceita parâmetros POST `user` e `password` para autenticação da API externa (se necessário).

## Como funciona o import
- A função `import_airports_from_api` lê a variável de ambiente `AIRPORT_DATA_URL`. Se `user` e `password` forem passados, usa-os; caso contrário, tentará `API_USER` e `API_PASSWORD` do ambiente.
- Faz uma requisição HTTP GET, processa o JSON retornado e usa `update_or_create` para manter os registros locais atualizados.
- Registra o resultado em `ImportLogModel` com contagem de criados/atualizados e detalhes de erro quando ocorrerem.

## Variáveis de ambiente importantes
- `AIRPORT_DATA_URL` — URL da API externa que retorna os dados de aeroportos em JSON.
- `API_USER` / `API_PASSWORD` — credenciais (opcionais) para Basic Auth se a API exigir.
- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` — configuração padrão do Django.

## Executando localmente
1. Criar e ativar o ambiente (usando Poetry, virtualenv, etc.).
2. Instalar dependências: `poetry install`.
3. Exportar as variáveis de ambiente necessárias (`AIRPORT_DATA_URL`, opcionalmente `API_USER` e `API_PASSWORD`).
4. Rodar migrações: `python manage.py migrate`.
5. Iniciar a aplicação: `python manage.py runserver`.
6. Para rodar o import manualmente via CLI: `python manage.py import_airports`.
7. Para acionar via endpoint: `POST /airports/import/` com `user` e `password` como dados do formulário (se a API exigir credenciais).

## Testes
Os testes unitários estão em `core/tests.py`. Para rodar apenas os testes do app `core`:

```bash
poetry run python manage.py test core
```

## Notas e decisões de design
- O projeto usa SQLite por padrão (configurado em `import_airports/settings.py`) para facilitar execução local. Pode ser alterado para Postgres/MySQL em produção.
- O `ImportLogModel` mantém arrays JSON com IATA criados/atualizados para facilitar auditoria.
- O endpoint de import está CSRF-exempt para facilitar chamadas externas via POST (ajuste se necessário para segurança em produção).

## Contribuindo
- Abra um PR com testes e descrição das alterações. Siga o padrão de código do repositório.

## Contato
- Théo Lopes