import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Send, Loader2, MessageCircle, Sparkles } from "lucide-react";
import { toast } from "sonner";

type Message = {
  role: "user" | "assistant";
  content: string;
  model?: string;
};

const CHAT_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/chat`;

const MODELS = [
  { id: "google/gemini-2.5-flash", name: "Sista Flash", description: "Quick & insightful", color: "sista-flash" },
  { id: "google/gemini-2.5-pro", name: "Sista Pro", description: "Deep wisdom", color: "sista-pro" },
  { id: "google/gemini-2.5-flash-lite", name: "Sista Lite", description: "Fast & caring", color: "sista-lite" },
] as const;

const Index = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const streamChat = async (model: { id: string; name: string }) => {
    const userMsg = messages.find((m) => m.role === "user" && !messages.some((msg) => msg.model === model.id && msg.role === "assistant"));
    if (!userMsg) return;

    try {
      const resp = await fetch(CHAT_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY}`,
        },
        body: JSON.stringify({ 
          messages: [{ role: "user", content: userMsg.content }],
          model: model.id 
        }),
      });

      if (!resp.ok || !resp.body) {
        if (resp.status === 429) {
          toast.error("Rate limit exceeded. Please try again later.");
          return;
        }
        if (resp.status === 402) {
          toast.error("Payment required. Please add funds.");
          return;
        }
        throw new Error("Failed to start stream");
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let textBuffer = "";
      let assistantSoFar = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        textBuffer += decoder.decode(value, { stream: true });

        let newlineIndex: number;
        while ((newlineIndex = textBuffer.indexOf("\n")) !== -1) {
          let line = textBuffer.slice(0, newlineIndex);
          textBuffer = textBuffer.slice(newlineIndex + 1);

          if (line.endsWith("\r")) line = line.slice(0, -1);
          if (line.startsWith(":") || line.trim() === "") continue;
          if (!line.startsWith("data: ")) continue;

          const jsonStr = line.slice(6).trim();
          if (jsonStr === "[DONE]") break;

          try {
            const parsed = JSON.parse(jsonStr);
            const content = parsed.choices?.[0]?.delta?.content as string | undefined;
            if (content) {
              assistantSoFar += content;
              setMessages((prev) => {
                const last = prev[prev.length - 1];
                const hasModel = prev.some((m) => m.model === model.id && m.role === "assistant");
                
                if (hasModel) {
                  return prev.map((m) =>
                    m.model === model.id && m.role === "assistant"
                      ? { ...m, content: assistantSoFar }
                      : m
                  );
                }
                return [...prev, { role: "assistant", content: assistantSoFar, model: model.id }];
              });
            }
          } catch {
            textBuffer = line + "\n" + textBuffer;
            break;
          }
        }
      }
    } catch (e) {
      console.error(e);
      toast.error(`Failed to get response from ${model.name}`);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      await Promise.all(MODELS.map((model) => streamChat(model)));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-warm">
      <div className="max-w-7xl mx-auto p-4 md:p-8">
        {/* Header */}
        <div className="text-center mb-8 pt-4">
          <div className="flex items-center justify-center gap-3 mb-3">
            <Sparkles className="w-8 h-8 text-primary" />
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              SistaChat
            </h1>
            <MessageCircle className="w-8 h-8 text-primary" />
          </div>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Pull up a chair, sis! Get advice from three wise perspectives at once. 
            It's like having your whole family around the table.
          </p>
        </div>

        {/* Chat Columns */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {MODELS.map((model) => {
            const modelMessages = messages.filter((m) => m.model === model.id);
            
            return (
              <Card key={model.id} className="h-[600px] flex flex-col shadow-md hover:shadow-glow transition-all">
                <CardHeader className="pb-3 border-b">
                  <CardTitle className="flex flex-col gap-2">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full bg-${model.color}`}></div>
                      <span className="text-xl">{model.name}</span>
                    </div>
                    <p className="text-sm font-normal text-muted-foreground">{model.description}</p>
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex-1 overflow-y-auto p-4 bg-gradient-warm">
                  <div className="space-y-4">
                    {messages
                      .filter((msg) => msg.role === "user" || msg.model === model.id)
                      .map((msg, idx) => (
                        <div
                          key={idx}
                          className={`p-4 rounded-xl transition-all ${
                            msg.role === "user"
                              ? "bg-primary text-primary-foreground ml-8 shadow-sm"
                              : `bg-card mr-8 shadow-sm border-l-4 border-${model.color}`
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                        </div>
                      ))}
                    <div ref={scrollRef} />
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Input Area */}
        <Card className="shadow-lg border-2 border-primary/20">
          <CardContent className="p-6">
            <div className="flex gap-3">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="What's on your mind? Ask away, and let the sistas share their wisdom..."
                className="min-h-[120px] text-base resize-none"
              />
              <Button
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                size="lg"
                className="h-auto bg-gradient-primary hover:opacity-90 transition-opacity shadow-md"
              >
                {isLoading ? (
                  <Loader2 className="h-6 w-6 animate-spin" />
                ) : (
                  <Send className="h-6 w-6" />
                )}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-3 text-center">
              Press Enter to send • Shift + Enter for new line
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Index;
