// Enhanced ChatInterface Component with API Integration
// This replaces your existing src/components/ChatInterface.tsx

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Send, MessageSquare, Clock, CheckCircle, Loader2 } from "lucide-react";
import { useDirectQuery, useVectorStoreStatus } from "@/hooks/useAPI";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  quality?: string;
  quality_score?: number;
  isLoading?: boolean;
}

export const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I'm your AI RFP assistant. Ask me anything about generating responses, or try one of the quick questions below.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState("");

  // API hooks
  const directQueryMutation = useDirectQuery();
  const { data: vectorStoreStatus } = useVectorStoreStatus();

  const quickQuestions = [
    "What are your company's core competencies?",
    "Describe your implementation methodology",
    "What's your approach to security and compliance?",
    "Tell me about your team's experience"
  ];

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    // Add user message and loading assistant message
    const loadingMessage: Message = {
      role: "assistant",
      content: "Generating response...",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isLoading: true
    };

    setMessages(prev => [...prev, userMessage, loadingMessage]);

    // Make API call
    directQueryMutation.mutate(
      { 
        query: input,
        top_k: 3,
        model: "llama3"
      },
      {
        onSuccess: (data) => {
          const assistantMessage: Message = {
            role: "assistant",
            content: data.data?.answer || "I apologize, but I couldn't generate a response at this time.",
            quality: data.data?.quality_status?.toLowerCase(),
            quality_score: data.data?.quality_score,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          };

          // Replace loading message with actual response
          setMessages(prev => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1] = assistantMessage;
            return newMessages;
          });
        },
        onError: (error) => {
          const errorMessage: Message = {
            role: "assistant",
            content: `Sorry, I encountered an error: ${error.message}`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          };

          // Replace loading message with error message
          setMessages(prev => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1] = errorMessage;
            return newMessages;
          });
        }
      }
    );

    setInput("");
  };

  const getQualityBadge = (quality?: string, score?: number) => {
    if (!quality) return null;
    
    const variants = {
      excellent: "default",
      good: "secondary",
      "needs-review": "destructive"
    } as const;

    return (
      <div className="flex items-center gap-1">
        <Badge variant={variants[quality as keyof typeof variants] || "secondary"}>
          {quality === "excellent" && <CheckCircle className="h-3 w-3 mr-1" />}
          {quality}
        </Badge>
        {score && (
          <span className="text-xs text-muted-foreground">
            {score.toFixed(1)}/10
          </span>
        )}
      </div>
    );
  };

  const isVectorStoreReady = vectorStoreStatus?.data?.ready_for_queries;

  return (
    <div className="grid md:grid-cols-3 gap-6 animate-fade-in">
      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Direct Query Interface
          </CardTitle>
          <CardDescription className="flex items-center justify-between">
            <span>Ask questions directly and get AI-generated responses instantly</span>
            {!isVectorStoreReady && (
              <Badge variant="outline" className="text-yellow-600">
                Knowledge Base Not Ready
              </Badge>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <ScrollArea className="h-[400px] pr-4">
            <div className="space-y-4">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-4 ${
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      <p className="text-sm flex-1">{msg.content}</p>
                      {msg.isLoading && (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs opacity-70 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {msg.timestamp}
                      </span>
                      {getQualityBadge(msg.quality, msg.quality_score)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>

          <div className="flex gap-2">
            <Input
              placeholder={
                isVectorStoreReady 
                  ? "Ask a question about your RFP..." 
                  : "Upload documents to knowledge base first..."
              }
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSend()}
              disabled={!isVectorStoreReady || directQueryMutation.isPending}
            />
            <Button 
              onClick={handleSend} 
              size="icon" 
              disabled={!isVectorStoreReady || directQueryMutation.isPending || !input.trim()}
            >
              {directQueryMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Quick Questions</CardTitle>
          <CardDescription>
            Common RFP questions to get started
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {quickQuestions.map((question, idx) => (
              <Button
                key={idx}
                variant="outline"
                className="w-full justify-start text-left h-auto py-3"
                onClick={() => setInput(question)}
                disabled={!isVectorStoreReady}
              >
                {question}
              </Button>
            ))}
          </div>
          
          {!isVectorStoreReady && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                💡 Upload documents to the Knowledge Base to enable AI queries
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};