
import { useState, useRef, useEffect } from 'react';
import { Send, Brain, BookOpen, MessageCircle, HelpCircle, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useTypingEffect } from '@/utils/animations';

type MessageType = 'user' | 'agent' | 'system';

interface Message {
  id: string;
  content: string;
  type: MessageType;
  timestamp: Date;
  isTyping?: boolean;
}

const mockResponses: Record<string, string> = {
  learning: "I've analyzed your suggestion on using Fibonacci retracement for short-term trading. From my historical data, this approach has 72% success rate when combined with volume analysis on established tokens. I'll incorporate this insight into my trading strategy. Thank you for the valuable input.",
  
  strategy: "Based on my recent performance with RSI-based entries, I've adjusted my strategy to use higher timeframe confirmations before entry. This has reduced false signals by 28% in the last 24 hours of testing.",
  
  question: "The current pattern recognition model I'm using has been trained on 2,458 historical patterns across 15,723 unique tokens. For triangle patterns specifically, my accuracy rate is 68% with a 3:1 risk-reward ratio when volume confirms the breakout.",
  
  feedback: "I understand your feedback about avoiding tokens with less than $50k liquidity. I've updated my filtering parameters to exclude these tokens. This should help avoid the slippage issues you've experienced with recent trades."
};

const generateId = () => Math.random().toString(36).substring(2, 9);

const ChatWithAgent = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: generateId(),
      content: "Hello! I'm your cryptocurrency trading assistant. How can I help you today?",
      type: 'agent',
      timestamp: new Date(Date.now() - 60000)
    }
  ]);
  
  const [inputValue, setInputValue] = useState('');
  const [currentTab, setCurrentTab] = useState('chat');
  const [isAgentThinking, setIsAgentThinking] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  
  // For typing effect in the latest agent message
  const latestAgentMessage = [...messages].reverse().find(m => m.type === 'agent' && m.isTyping);
  const typingEffect = useTypingEffect(latestAgentMessage?.content || '', 20);
  
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTo({ top: 100000, behavior: 'smooth' });
    }
  }, [messages]);
  
  const handleSendMessage = () => {
    if (!inputValue.trim()) return;
    
    const newUserMessage: Message = {
      id: generateId(),
      content: inputValue,
      type: 'user',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    setInputValue('');
    setIsAgentThinking(true);
    
    // Simulate agent typing response
    setTimeout(() => {
      setIsAgentThinking(false);
      
      // Determine response type based on content
      let responseContent = '';
      
      if (inputValue.toLowerCase().includes('learn') || inputValue.toLowerCase().includes('study')) {
        responseContent = mockResponses.learning;
      } else if (inputValue.toLowerCase().includes('strategy') || inputValue.toLowerCase().includes('approach')) {
        responseContent = mockResponses.strategy;
      } else if (inputValue.toLowerCase().includes('?') || inputValue.toLowerCase().includes('how') || inputValue.toLowerCase().includes('what')) {
        responseContent = mockResponses.question;
      } else {
        responseContent = mockResponses.feedback;
      }
      
      const newAgentMessage: Message = {
        id: generateId(),
        content: responseContent,
        type: 'agent',
        timestamp: new Date(),
        isTyping: true
      };
      
      setMessages(prev => [...prev, newAgentMessage]);
      
      // Remove typing indicator after effect completes
      setTimeout(() => {
        setMessages(prev => 
          prev.map(msg => 
            msg.id === newAgentMessage.id 
              ? { ...msg, isTyping: false } 
              : msg
          )
        );
      }, responseContent.length * 20 + 500);
    }, 1500);
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const renderMessage = (message: Message) => {
    const isLatestAgentTyping = message.type === 'agent' && message.isTyping;
    
    return (
      <div 
        key={message.id} 
        className={`mb-4 ${
          message.type === 'user' 
            ? 'ml-auto max-w-[80%]' 
            : 'mr-auto max-w-[80%]'
        }`}
      >
        <div className={`flex items-start gap-2 ${
          message.type === 'user' ? 'flex-row-reverse' : 'flex-row'
        }`}>
          {message.type === 'user' ? (
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              U
            </div>
          ) : (
            <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center text-secondary-foreground">
              <Brain className="h-4 w-4" />
            </div>
          )}
          
          <div>
            <div className={`rounded-lg px-3 py-2 ${
              message.type === 'user'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary/40 text-foreground'
            }`}>
              {isLatestAgentTyping ? typingEffect : message.content}
              {isLatestAgentTyping && (
                <span className="inline-block w-1.5 h-4 ml-0.5 align-middle bg-current animate-pulse"></span>
              )}
            </div>
            
            <div className="text-xs text-muted-foreground mt-1">
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  return (
    <div className="glass-panel rounded-lg overflow-hidden h-[500px] flex flex-col">
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-medium">Agent Communication</h3>
        </div>
        
        <Badge variant="outline" className="bg-primary/10 text-primary">
          <Brain className="w-3 h-3 mr-1" />
          Online
        </Badge>
      </div>
      
      <Tabs value={currentTab} onValueChange={setCurrentTab} className="flex-1 flex flex-col">
        <TabsList className="px-4 pt-2 bg-transparent justify-start">
          <TabsTrigger value="chat" className="flex items-center gap-1.5 data-[state=active]:bg-primary/10">
            <MessageCircle className="w-4 h-4" />
            <span>Chat</span>
          </TabsTrigger>
          
          <TabsTrigger value="materials" className="flex items-center gap-1.5 data-[state=active]:bg-primary/10">
            <BookOpen className="w-4 h-4" />
            <span>Study Materials</span>
          </TabsTrigger>
          
          <TabsTrigger value="help" className="flex items-center gap-1.5 data-[state=active]:bg-primary/10">
            <HelpCircle className="w-4 h-4" />
            <span>Help</span>
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="chat" className="flex-1 flex flex-col mt-0 pt-3">
          <ScrollArea className="flex-1 px-4" ref={scrollAreaRef}>
            <div className="space-y-4">
              {messages.map(renderMessage)}
              
              {isAgentThinking && (
                <div className="mb-4 mr-auto max-w-[80%]">
                  <div className="flex items-start gap-2">
                    <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center text-secondary-foreground">
                      <Brain className="h-4 w-4" />
                    </div>
                    
                    <div>
                      <div className="rounded-lg px-3 py-2 bg-secondary/40 text-foreground">
                        <div className="flex space-x-1">
                          <div className="h-2 w-2 rounded-full bg-current animate-bounce"></div>
                          <div className="h-2 w-2 rounded-full bg-current animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          <div className="h-2 w-2 rounded-full bg-current animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
          
          <div className="p-4 border-t border-border">
            <div className="flex gap-2">
              <Input
                placeholder="Ask a question or provide feedback..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyPress}
                className="flex-1"
                disabled={isAgentThinking}
              />
              
              <Button 
                onClick={handleSendMessage} 
                disabled={!inputValue.trim() || isAgentThinking}
              >
                <Send className="h-4 w-4" />
                <span className="sr-only">Send</span>
              </Button>
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="materials" className="flex-1 overflow-auto mt-0 p-4">
          <div className="space-y-4">
            <div className="bg-primary/10 rounded-lg p-3">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-primary/20 rounded-full">
                  <BookOpen className="h-5 w-5 text-primary" />
                </div>
                
                <div>
                  <h4 className="font-medium">Trading Education</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    Provide study materials for the AI to improve its trading knowledge.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="grid gap-3">
              <div className="border rounded-lg p-3 hover:bg-muted/50 transition-colors">
                <div className="flex items-center justify-between">
                  <h5 className="font-medium">Technical Analysis Fundamentals</h5>
                  <Badge variant="outline">PDF</Badge>
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  A guide covering RSI, MACD, Bollinger Bands and more.
                </p>
                <Button variant="ghost" size="sm" className="mt-2">
                  <Sparkles className="h-4 w-4 mr-1" />
                  Share with Agent
                </Button>
              </div>
              
              <div className="border rounded-lg p-3 hover:bg-muted/50 transition-colors">
                <div className="flex items-center justify-between">
                  <h5 className="font-medium">Smart Contract Audit Checklist</h5>
                  <Badge variant="outline">PDF</Badge>
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  Comprehensive guide for detecting suspicious contracts.
                </p>
                <Button variant="ghost" size="sm" className="mt-2">
                  <Sparkles className="h-4 w-4 mr-1" />
                  Share with Agent
                </Button>
              </div>
              
              <div className="border rounded-lg p-3 hover:bg-muted/50 transition-colors">
                <div className="flex items-center justify-between">
                  <h5 className="font-medium">Liquidity Pool Analysis</h5>
                  <Badge variant="outline">Video</Badge>
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  How to detect manipulation and fake volume.
                </p>
                <Button variant="ghost" size="sm" className="mt-2">
                  <Sparkles className="h-4 w-4 mr-1" />
                  Share with Agent
                </Button>
              </div>
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="help" className="flex-1 overflow-auto mt-0 p-4">
          <div className="space-y-4">
            <div className="bg-muted/50 rounded-lg p-4">
              <h4 className="font-medium mb-2">How to communicate with the AI Agent</h4>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <Badge className="mt-0.5">Ask</Badge>
                  <p>Ask questions about trading strategies, patterns, or technical analysis</p>
                </li>
                <li className="flex items-start gap-2">
                  <Badge className="mt-0.5">Feedback</Badge>
                  <p>Provide feedback on trades the AI has executed</p>
                </li>
                <li className="flex items-start gap-2">
                  <Badge className="mt-0.5">Teach</Badge>
                  <p>Share insights or strategies for the AI to learn from</p>
                </li>
                <li className="flex items-start gap-2">
                  <Badge className="mt-0.5">Review</Badge>
                  <p>Request analysis of specific trading patterns or tokens</p>
                </li>
              </ul>
            </div>
            
            <div className="border rounded-lg p-4">
              <h4 className="font-medium mb-2">Example Questions</h4>
              <div className="space-y-2 text-sm">
                <p className="bg-muted p-2 rounded">"What indicators are you currently using for entry signals?"</p>
                <p className="bg-muted p-2 rounded">"Can you explain your risk management strategy?"</p>
                <p className="bg-muted p-2 rounded">"I've noticed that X coin is showing Y pattern. What's your analysis?"</p>
                <p className="bg-muted p-2 rounded">"Please explain how you detect fake volume in new tokens"</p>
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ChatWithAgent;
