import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Bot, Terminal, Cpu, Search, AlertCircle } from 'lucide-react';
import { api } from '@/services/api';

interface ActivityLog {
  id: number;
  timestamp: string;
  type: 'scan' | 'analysis' | 'decision' | 'action' | 'alert';
  message: string;
  details?: string;
}

const AgentActivityMonitor = () => {
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [newActivities, setNewActivities] = useState<ActivityLog[]>([]);
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
  
  useEffect(() => {
    // Initial data fetch
    fetchActivities();
    
    // Setup polling for new activities
    const interval = setInterval(() => {
      fetchNewActivities();
    }, 10000); // Poll every 10 seconds
    
    setPollingInterval(interval);
    
    return () => {
      if (pollingInterval) clearInterval(pollingInterval);
    };
  }, []);
  
  const fetchActivities = async () => {
    setIsLoading(true);
    try {
      const data = await api.agentActivity.getAll();
      setActivities(data);
    } catch (error) {
      console.error('Failed to fetch agent activities:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const fetchNewActivities = async () => {
    try {
      // Get only the most recent activities
      const recent = await api.agentActivity.getRecent(5);
      
      // Filter out activities we already have
      const newOnes = recent.filter(activity => 
        !activities.some(a => a.id === activity.id)
      );
      
      if (newOnes.length > 0) {
        setNewActivities(newOnes);
        setActivities(prev => [...newOnes, ...prev].slice(0, 100));
      }
    } catch (error) {
      console.error('Failed to fetch new activities:', error);
    }
  };
  
  const filteredActivities = activeFilter === 'all' 
    ? activities 
    : activities.filter(a => a.type === activeFilter);
    
  const getIconForType = (type: ActivityLog['type']) => {
    switch (type) {
      case 'scan': return <Search className="w-4 h-4" />;
      case 'analysis': return <Cpu className="w-4 h-4" />;
      case 'decision': return <Terminal className="w-4 h-4" />;
      case 'action': return <Bot className="w-4 h-4" />;
      case 'alert': return <AlertCircle className="w-4 h-4" />;
    }
  };
  
  const getColorForType = (type: ActivityLog['type']) => {
    switch (type) {
      case 'scan': return 'bg-blue-500/10 text-blue-500';
      case 'analysis': return 'bg-indigo-500/10 text-indigo-500';
      case 'decision': return 'bg-purple-500/10 text-purple-500';
      case 'action': return 'bg-green-500/10 text-green-500';
      case 'alert': return 'bg-red-500/10 text-red-500';
    }
  };
  
  return (
    <div className="glass-panel rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-medium">Agent Activity Monitor</h3>
        </div>
        {newActivities.length > 0 && (
          <Badge variant="secondary" className="animate-pulse">
            {newActivities.length} new {newActivities.length === 1 ? 'activity' : 'activities'}
          </Badge>
        )}
      </div>
      
      <div className="p-6">
        <Tabs defaultValue="all" value={activeFilter} onValueChange={setActiveFilter}>
          <TabsList className="mb-4 grid grid-cols-6">
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="scan">Scan</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
            <TabsTrigger value="decision">Decision</TabsTrigger>
            <TabsTrigger value="action">Action</TabsTrigger>
            <TabsTrigger value="alert">Alert</TabsTrigger>
          </TabsList>
          
          <TabsContent value={activeFilter} className="mt-0">
            <ScrollArea className="h-[400px] pr-4">
              <div className="space-y-3">
                {filteredActivities.map((activity) => (
                  <div 
                    key={activity.id} 
                    className={`border rounded-md p-3 ${
                      newActivities.some(a => a.id === activity.id) 
                        ? 'animate-pulse bg-muted/40' 
                        : ''
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-full mt-0.5 ${getColorForType(activity.type)}`}>
                          {getIconForType(activity.type)}
                        </div>
                        <div>
                          <div className="font-medium">{activity.message}</div>
                          {activity.details && (
                            <div className="text-sm text-muted-foreground mt-1">
                              {activity.details}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground font-mono">
                        {new Date(activity.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
        
        <div className="mt-4 text-xs text-muted-foreground">
          Monitoring real-time agent activities. The AI agent processes approximately 250 tokens per minute and updates the activity log continuously.
        </div>
      </div>
    </div>
  );
};

export default AgentActivityMonitor;
