import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from llama_index.llms.groq import Groq

from vetorizacao import vetorizar_texto, busca_vetorial

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI(title="API Q&A Filmes")
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
buscador,llm = None, None

class ChatRequest(BaseModel):
    pergunta: str

@app.on_event("startup")
def iniciar_sist():
    global llm
    print("--- 🚀 TENTANDO INICIAR O SISTEMA ---")
    
    # 1. Verifica se a chave foi lida do arquivo .env
    if not GROQ_API_KEY:
        print("❌ ERRO CRÍTICO: A variável GROQ_API_KEY está vazia ou None!")
        print("   -> Verifique se o arquivo .env existe na mesma pasta.")
        print("   -> Verifique se tem algo escrito dentro dele.")
        return

    print(f"🔑 Chave encontrada: {GROQ_API_KEY[:5]}... (oculto)")

    try:
        # 2. Tenta conectar na Groq
        print("🔌 Conectando aos servidores da Groq...")
        llm = Groq(model='llama-3.1-8b-instant', api_key=GROQ_API_KEY)
        
        # 3. Teste rápido para ver se a chave funciona de verdade
        # Fazemos uma pergunta boba só pra testar a conexão
        teste = llm.complete("Diga oi")
        print(f"✅ CONEXÃO BEM SUCEDIDA! O Groq respondeu: '{teste.text.strip()}'")
        
    except Exception as e:
        print(f"\n❌ ERRO FATAL AO CONECTAR NO GROQ:")
        print(f"   -> {str(e)}")
        print("   -> Verifique sua internet ou se a chave API é válida.")
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

            titulo = filme.get('title') or filme.get('Nome_Filme') or "N/A"
            genero = filme.get('genres') or filme.get('Generos') or "N/A"
            nota = filme.get('media_nota') or filme.get('Nota') or "N/A"
            detalhes = filme.get('contexto_completo') or filme.get('Detalhes') or ""

            trecho = f"- Filme: {titulo} | Gêneros: {genero} | Nota: {nota}\n"
            trecho += f"  Detalhes: {detalhes}\n\n"
            

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