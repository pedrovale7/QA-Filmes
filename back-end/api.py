import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from llama_index.core.llms import ChatMessage, MessageRole
from vetorizacao import busca_vetorial

os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

historico_conversas = []
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

    global llm, historico_conversas
    if not GROQ_API_KEY:
        print("Chave inválida para o Groq")
        return

    try:
        print("Conectando aos servidores da Groq...")
        llm = Groq(model='llama-3.1-8b-instant', api_key=GROQ_API_KEY)        
    except Exception as e:
        print(f"Erro de conexão do Groq: {e}")
        llm = None

    # Definição de prompt inicial no startup    
    if not historico_conversas:
        sys_prompt = f"""
        Você é um especialista em filmes. Use apenas os dados de sua base de treinamento e para responder perguntas do usuário sobre sugestões de filmes.
        Qualquer pergunta sobre qualquer outro assunto deve ser rejeitada educadamente explicando que você apenas recomenda filmes.
        Tenha uma comunicação leve e amigável e recomende os filmes listados explicando o porque da sua desicão.
        REGRAS DE RESPOSTA:
        1. NÃO faça introduções longas (como "Olá", "Ótima escolha").
        2. Limite a resposta a no máximo 2 ou 3 frases por filme.
        3. Diga apenas: Nome do Filme + Nota + Motivo breve da recomendação.
        4. Se houver mais de um filme, separe claramente.
        """
        historico_conversas.append(ChatMessage(role=MessageRole.SYSTEM, content=sys_prompt))


@app.get("/inicio")
def iniciar_chat():
    global historico_conversas
    
    # Prompt inicial de boas-vindas para direcionar experiência do usuário
    mensagem_inicial = "Olá! Estou aqui para ajudar você a encontrar o filme perfeito. Qual gênero ou tipo de filme você gostaria de assistir hoje?"    
    if len(historico_conversas) == 1: # Só tem o System Prompt
        historico_conversas.append(ChatMessage(role=MessageRole.ASSISTANT, content=mensagem_inicial))
    
    return {"resposta": mensagem_inicial}

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
        Considere os seguintes filmes encontrados no banco de dados:
        {contexto}
        
        Com base nesses filmes, responda à seguinte pergunta do usuário se, e somente se, tratar-se de uma solicitação de recomendação de filmes. Caso contrário, deve-se responder conforme orientado no prompt de sistema.
        
        Pergunta do usuário:
        {pergunta_usuario}
        """
        
        # Adiciona mensagens anteriores ao histórico
        msg_usuario = ChatMessage(role=MessageRole.USER, content=prompt)
        historico_conversas.append(msg_usuario)

        #resposta = llm.complete(prompt)
        #return {"resposta": resposta.text}

        resposta = llm.chat(historico_conversas)
        historico_conversas.append(resposta.message)
        return {"resposta": resposta.message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/limpar")
def limpar_historico():
    global historico_conversas, llm
    historico_conversas = [] # Zera a lista
    
    # Reinicializa com o System Prompt
    sys_prompt = f"""
    Você é um especialista em filmes. Use apenas os dados de sua base de treinamento e para responder perguntas do usuário sobre sugestões de filmes.
    Qualquer pergunta sobre qualquer outro assunto deve ser rejeitada educadamente explicando que você apenas recomenda filmes.
    Tenha uma comunicação leve e amigável e recomende os filmes listados explicando o porque da sua desicão.
    REGRAS DE RESPOSTA:
    1. NÃO faça introduções longas (como "Olá", "Ótima escolha").
    2. Limite a resposta a no máximo 2 ou 3 frases por filme.
    3. Diga apenas: Nome do Filme + Nota + Motivo breve da recomendação.
    4. Se houver mais de um filme, separe claramente.
    """
    historico_conversas.append(ChatMessage(role=MessageRole.SYSTEM, content=sys_prompt))
    
    return {"status": "Histórico limpo"}