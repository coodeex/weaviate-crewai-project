'use client';
import { useState, useRef, useEffect } from 'react';
import { CornerDownLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ChatBubble, ChatBubbleAvatar, ChatBubbleMessage } from '@/components/ui/chat-bubble';
import { ChatMessageList } from '@/components/ui/chat-message-list';
import { ChatInput } from '@/components/ui/chat-input';

export default function ChatPage() {
  // State for user input and chat history
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<{ role: 'user' | 'bot'; text: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading]);

  // Handle sending a message
  async function handleSend(e?: React.FormEvent) {
    if (e) e.preventDefault();
    if (!input.trim()) return;
    const userMessage = input;
    setMessages((msgs) => [...msgs, { role: 'user', text: userMessage }]);
    setInput('');
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      });
      if (!res.ok) throw new Error('Network response was not ok');
      const data = await res.json();
      setMessages((msgs) => [...msgs, { role: 'bot', text: data.response }]);
    } catch (err: any) {
      setMessages((msgs) => [...msgs, { role: 'bot', text: 'Error: ' + (err.message || 'Unknown error') }]);
    } finally {
      setLoading(false);
    }
  }

  // Handle Enter/Shift+Enter in textarea
  function handleInputKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-zinc-900 via-zinc-800 to-zinc-900 p-4">
      <div className="w-full max-w-xl bg-zinc-950/80 rounded-2xl shadow-2xl p-0 flex flex-col gap-0 border border-zinc-800">
        {/* Chat messages */}
        <div className="flex-1 min-h-[400px] max-h-[600px] h-[400px] overflow-y-auto px-2 py-4">
          <ChatMessageList>
            {messages.length === 0 && (
              <div className="text-zinc-500 text-center pt-12">Start the conversation!</div>
            )}
            {messages.map((msg, idx) => (
              <ChatBubble key={idx} variant={msg.role === 'user' ? 'sent' : 'received'}>
                <ChatBubbleAvatar
                  fallback={msg.role === 'user' ? 'U' : 'A'}
                />
                <ChatBubbleMessage variant={msg.role === 'user' ? 'sent' : 'received'}>
                  {msg.text}
                </ChatBubbleMessage>
              </ChatBubble>
            ))}
            {loading && (
              <ChatBubble variant="received">
                <ChatBubbleAvatar fallback="AI" />
                <ChatBubbleMessage isLoading />
              </ChatBubble>
            )}
            <div ref={messagesEndRef} />
          </ChatMessageList>
        </div>
        {/* Input bar */}
        <div className="p-4 border-t border-zinc-800 bg-zinc-950/90">
          <form onSubmit={handleSend} className="relative rounded-lg border bg-zinc-900 focus-within:ring-1 focus-within:ring-violet-500 p-1">
            <ChatInput
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleInputKeyDown}
              placeholder="Type your message..."
              className="min-h-12 resize-none rounded-lg bg-zinc-900 border-0 p-3 shadow-none focus-visible:ring-0 text-zinc-100"
              disabled={loading}
              autoFocus
            />
            <div className="flex items-center p-3 pt-0 justify-end">
              <Button type="submit" size="sm" className="ml-auto gap-1.5" disabled={loading || !input.trim()}>
                Send
                <CornerDownLeft className="size-3.5" />
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
