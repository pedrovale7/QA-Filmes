import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from llama_index.llms.groq import Groq

from vetorizacao import vetorizar_texto, busca_vetorial

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI(title="API Q&A Filmes")

buscador,llm = None, None

class ChatRequest(BaseModel):
    pergunta: str

@app.on_event("startup")
def iniciar_sist():

    global llm
    if not GROQ_API_KEY:
        print("Chave inválida para o Groq")
        return

    try:

        print("Conectando aos servidores da Groq...")
        llm = Groq(model='llama-3.1-8b-instant', api_key=GROQ_API_KEY)
        
    except Exception as e:
        print(f"Erro de conexão do Groq: {e}")
        llm = None

@app.post("/chat")
def chat_endpoint(request: ChatRequest):

    if llm is None:
        raise HTTPException(status_code=500, detail="O modelo LLM não foi carregado.")
    
    pergunta_usuario = request.pergunta.lower().strip()
    
    try:
        respostas = busca_vetorial(pergunta_usuario, top_k=5)
        contexto = "" 

        for filme in respostas:

            titulo = filme.get('Nome_Filme') or ""
            genero = filme.get('Generos') or ""
            nota = filme.get('Nota') or ""
            detalhes = filme.get('Detalhes') or ""

            trecho = f'''
                Filme: {titulo} \n 
                Gêneros: {genero}\n
                Nota: {nota}\n 
                Detalhes: {detalhes}\n   
                '''
            contexto += trecho
        
        prompt = f"""
        Você é um especialista em filmes. Use apenas os dados abaixo para responder perguntas do usuário sobre sugestões de filmes
        Tenha uma comunicação leve e amigável e recomende os filmes listados explicando o porque da sua desicão.

        REGRAS DE RESPOSTA:
        1. NÃO faça introduções longas (como "Olá", "Ótima escolha").
        2. Limite a resposta a no máximo 2 ou 3 frases por filme.
        3. Diga apenas: Nome do Filme + Nota + Motivo breve da recomendação.
        4. Se houver mais de um filme, separe claramente.

        SISTEMA: {contexto}
        PERGUNTA DO USUÁRIO: {pergunta_usuario}"""
        
        resposta = llm.complete(prompt)
        
        return {"resposta": resposta.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))