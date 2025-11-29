import { useState, useEffect } from 'react'
import './App.css'
type ChatMessage = {
  type: 'user' | 'bot' | 'error';
  text: string;
};

function App() {
  const [userInput, setUserInput] = useState('');
  const [chatLog, setChatLog] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchWelcomeMessage = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/inicio');
      if (!response.ok) {
        throw new Error('Erro ao conectar com o servidor');
      }
      const data = await response.json();
      
      const botMessage = { type: 'bot', text: data.resposta } as ChatMessage;
      setChatLog([botMessage]);
      
      // Salva no localStorage
      localStorage.setItem('chatLog', JSON.stringify([botMessage]));
      
    } catch (error) {
      console.error('Erro ao iniciar chat:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const storedChatLog = localStorage.getItem('chatLog');
    if (storedChatLog) {
      setChatLog(JSON.parse(storedChatLog))
    } else {
      fetchWelcomeMessage();
    }
  }, []);

  const clearChat = async () => {
    try {
        // 1. Avisa o backend para esquecer a memória
        await fetch('http://127.0.0.1:8000/limpar', { method: 'DELETE' });        
        // 2. Limpa o navegador
        localStorage.removeItem('chatLog');
        setChatLog([]);
        // 3. Traz a mensagem de boas-vindas novamente
        fetchWelcomeMessage();
    } catch (error) {
        console.error("Erro ao limpar histórico:", error);
    }
  };

  const handleSubmit = async (event: any) => {
    event.preventDefault(); // impede a pagina de regarregar
    if (!userInput.trim()) return;

    const userMessage = { type: 'user', text: userInput } as ChatMessage;
    const newChatLog = [...chatLog, userMessage]; // append to chatlog
    setChatLog(newChatLog);
    setUserInput('');
    setLoading(true)

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-type': 'application/json' },
        body: JSON.stringify({ pergunta: userInput }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const botMessage = { type: 'bot', text: data.resposta } as ChatMessage

      const finalChatLog = [...newChatLog, botMessage];
      setChatLog(finalChatLog);

      localStorage.setItem('chatLog', JSON.stringify(finalChatLog));
    } catch (error) {
      console.error('Error fetching chat response:', error);
      const errorMessage = { type: 'error', text: 'Sorry, something went wrong. Please try again.' } as ChatMessage;
      setChatLog(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="header-container" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
      {/* Container do Cabeçalho Centralizado */}
      <div style={{
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        gap: '10px',
        marginBottom: '20px'
      }}>
        <h1 style={{ margin: 0 }}>AI Chatbot - Filmes</h1>
        
        <button 
          onClick={clearChat} 
          style={{
            backgroundColor: '#ff4444', 
            color: 'white', 
            padding: '8px 16px',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            fontSize: '0.9rem'
          }}
        >
          Limpar Conversa
        </button>
      </div>
      </div>
      <div className="chat-window">
        {chatLog.map((message, index) => (
          <div key={index} className={`message ${message.type}`}>
            {message.text}
          </div>
        ))}
        {loading && <div className="message bot">Loading...</div>}
      </div>
      <form onSubmit={handleSubmit} className="chat-form">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>Send</button>
      </form>
    </div>
  );

}

export default App
