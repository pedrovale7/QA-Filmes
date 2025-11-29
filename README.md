# QA-Filmes

## Requisitos
+ Necessário ter npm instalado na máquina.
+ Necessário ter python e gerenciador de ambientes instalado (pyenv, conda, mamba, etc)
+ Necessário criar uma chave de api grok no [site oficial](https://console.groq.com/home). Essa operação é gratuita. Após isso, deve-se incluir um arquivo `.env`, no diretório `back-end` com o seguinte conteúdo:
    ```
    GROQ_API_KEY=gsk_SUA_APIKEY_SEM_ASPAS
    ```

## Para rodar o front end:

```bash
$ cd front-end
$ npm install
$ npm run dev
```

## Para rodar o backend:
1. Entre no .venv (ou outro ambiente virtual criado). No nosso exemplo, ele se chama `env_paa`.
2. No diretório principal:
    ```bash
    (env_paa) $ pip install -r ./requirements.txt
    ```
3. Mudar para diretório do back-end e executar uvicorn: 
    ```bash
    $ cd back-end
    $ uvicorn api:app --reload
    ```