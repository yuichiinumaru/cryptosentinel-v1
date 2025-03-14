
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Agent, Message, agency } from '@/lib/agencySwarm';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Bot, ChevronRight, Users, MessageSquare, Zap } from 'lucide-react';

const AgentTeam = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeTab, setActiveTab] = useState('agents');
  
  useEffect(() => {
    // Load agents
    setAgents(agency.getAgents());
    
    // Load initial messages
    setMessages(agency.getMessages());
    
    // Subscribe to new messages
    const handleNewMessage = (message: Message) => {
      setMessages(prev => [message, ...prev].slice(0, 50));
    };
    
    agency.on('message', handleNewMessage);
    
    return () => {
      agency.off('message', handleNewMessage);
    };
  }, []);
  
  const getAgentColor = (agentId: string) => {
    switch (agentId) {
      case 'market-analyst': return 'bg-blue-500/10 text-blue-500';
      case 'trader': return 'bg-green-500/10 text-green-500';
      case 'learning-manager': return 'bg-purple-500/10 text-purple-500';
      case 'manager': return 'bg-amber-500/10 text-amber-500';
      default: return 'bg-gray-500/10 text-gray-500';
    }
  };
  
  const getAgentIcon = (agentId: string) => {
    switch (agentId) {
      case 'market-analyst': return 'MA';
      case 'trader': return 'TR';
      case 'learning-manager': return 'LM';
      case 'manager': return 'MG';
      default: return 'AI';
    }
  };
  
  return (
    <div className="glass-panel rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Users className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-medium">Agent Team</h3>
        </div>
        <Badge variant="outline" className="bg-primary/10">
          <Zap className="w-3 h-3 mr-1" />
          Active
        </Badge>
      </div>
      
      <div className="p-4">
        <Tabs defaultValue={activeTab} value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-2 mb-4">
            <TabsTrigger value="agents">
              <Users className="w-4 h-4 mr-2" />
              Team
            </TabsTrigger>
            <TabsTrigger value="communications">
              <MessageSquare className="w-4 h-4 mr-2" />
              Communications
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="agents" className="space-y-4">
            {agents.map(agent => (
              <Card key={agent.id}>
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-3">
                      <Avatar className={getAgentColor(agent.id)}>
                        <AvatarFallback>{getAgentIcon(agent.id)}</AvatarFallback>
                      </Avatar>
                      <div>
                        <CardTitle className="text-base">{agent.name}</CardTitle>
                        <CardDescription>{agent.role}</CardDescription>
                      </div>
                    </div>
                    <Badge variant={agent.isActive ? "default" : "outline"}>
                      {agent.isActive ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">{agent.description}</p>
                  <h4 className="text-xs font-semibold mb-2">Tools:</h4>
                  <div className="flex flex-wrap gap-1">
                    {agent.tools.slice(0, 5).map(tool => (
                      <Badge key={tool} variant="outline" className="text-xs">
                        {tool}
                      </Badge>
                    ))}
                    {agent.tools.length > 5 && (
                      <Badge variant="outline" className="text-xs">
                        +{agent.tools.length - 5} more
                      </Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>
          
          <TabsContent value="communications" className="mt-0">
            <ScrollArea className="h-[400px] pr-4">
              <div className="space-y-3">
                {messages.map(message => {
                  const agent = agents.find(a => a.id === message.agentId);
                  
                  return (
                    <div
                      key={message.id}
                      className="flex gap-3 p-3 border rounded-md"
                    >
                      <Avatar className={getAgentColor(message.agentId)}>
                        <AvatarFallback>{getAgentIcon(message.agentId)}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start">
                          <h4 className="font-medium text-sm">{agent?.name || 'Unknown Agent'}</h4>
                          <span className="text-xs text-muted-foreground">
                            {message.timestamp.toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-sm mt-1">{message.content}</p>
                      </div>
                    </div>
                  );
                })}
                
                {messages.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No communications yet
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AgentTeam;
