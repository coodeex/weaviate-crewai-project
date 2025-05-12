'use client';
import { useState } from 'react';

export default function ChatPage() {
  // State for user input and chat history
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<{ role: 'user' | 'bot'; text: string }[]>([]);
  const [loading, setLoading] = useState(false);

  // Handle sending a message
  async function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;
    const userMessage = input;
    setMessages((msgs) => [...msgs, { role: 'user', text: userMessage }]);
    setInput('');
    setLoading(true);
    // Simulate bot response (replace with real API call)
    setTimeout(() => {
      setMessages((msgs) => [...msgs, { role: 'bot', text: `Echo: ${userMessage}` }]);
      setLoading(false);
    }, 800);
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-4">
      <div className="w-full max-w-md bg-white rounded shadow p-4 flex flex-col gap-4">
        <div className="flex-1 overflow-y-auto min-h-[300px] max-h-[400px] border-b pb-2 mb-2">
          {messages.length === 0 && (
            <div className="text-gray-400 text-center">Start the conversation!</div>
          )}
          {messages.map((msg, idx) => (
            <div key={idx} className={msg.role === 'user' ? 'text-right' : 'text-left'}>
              <span className={msg.role === 'user' ? 'bg-blue-100 text-blue-800 rounded px-2 py-1 inline-block my-1' : 'bg-gray-200 text-gray-800 rounded px-2 py-1 inline-block my-1'}>
                {msg.text}
              </span>
            </div>
          ))}
          {loading && <div className="text-gray-400 text-sm">Bot is typing...</div>}
        </div>
        <form onSubmit={handleSend} className="flex gap-2">
          <input
            className="flex-1 border rounded px-3 py-2 focus:outline-none focus:ring focus:border-blue-300"
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={loading}
            autoFocus
          />
          <button
            className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
            type="submit"
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
