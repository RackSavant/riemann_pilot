import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send } from 'lucide-react';
import { useState } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  model?: string;
}

interface ModelChatPanelProps {
  modelName: string;
  messages: Message[];
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
}

export const ModelChatPanel = ({ modelName, messages, onSendMessage, isLoading }: ModelChatPanelProps) => {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim()) {
      onSendMessage(input);
      setInput('');
    }
  };

  return (
    <Card className="flex flex-col h-full border shadow-sm">
      <div className="p-3 border-b bg-muted/30">
        <h3 className="font-medium text-sm text-foreground">{modelName}</h3>
        <p className="text-xs text-muted-foreground">{messages.filter(m => m.role === 'user').length} / 5 turns</p>
      </div>
      
      <ScrollArea className="flex-1 p-3">
        <div className="space-y-3">
          {messages.length === 0 ? (
            <div className="text-center text-muted-foreground text-sm py-8">
              Start conversation
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`p-2.5 rounded text-sm ${
                  msg.role === 'user'
                    ? 'bg-primary/5 border border-primary/10'
                    : 'bg-muted/50'
                }`}
              >
                <div className="text-xs font-medium mb-1 text-muted-foreground">
                  {msg.role === 'user' ? 'You' : msg.model || modelName}
                </div>
                <div>{msg.content}</div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="bg-muted/50 p-2.5 rounded">
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 rounded-full bg-primary/50 animate-pulse" />
                <div className="w-1.5 h-1.5 rounded-full bg-primary/50 animate-pulse delay-75" />
                <div className="w-1.5 h-1.5 rounded-full bg-primary/50 animate-pulse delay-150" />
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
      
      <div className="p-3 border-t bg-muted/10">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type message..."
            disabled={messages.filter(m => m.role === 'user').length >= 5 || isLoading}
            className="text-sm"
          />
          <Button 
            onClick={handleSend} 
            disabled={!input.trim() || messages.filter(m => m.role === 'user').length >= 5 || isLoading}
            size="icon"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
};
