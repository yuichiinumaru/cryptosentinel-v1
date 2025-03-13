
import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Bot, Terminal, Cpu, Search, AlertCircle } from 'lucide-react';

interface ActivityLog {
  id: number;
  timestamp: string;
  type: 'scan' | 'analysis' | 'decision' | 'action' | 'alert';
  message: string;
  details?: string;
}

const mockActivities: ActivityLog[] = [
  {
    id: 1,
    timestamp: new Date().toISOString(),
    type: 'scan',
    message: 'Scanning DexScreener for new tokens',
    details: 'Filtering by 24h volume > $10,000'
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 35000).toISOString(),
    type: 'analysis',
    message: 'Analyzing PEPE token price movement',
    details: 'RSI: 72.4, MACD: Bullish crossover, Volume: Increasing'
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 95000).toISOString(),
    type: 'decision',
    message: 'Evaluating entry for ShibaGF token',
    details: 'Contract age: 3 days, Liquidity: $450K, Owner renounced: Yes'
  },
  {
    id: 4,
    timestamp: new Date(Date.now() - 150000).toISOString(),
    type: 'action',
    message: 'Bought ShibaGF token for 0.15 ETH',
    details: 'Entry price: $0.00000082, Stop loss: $0.00000068, Target: $0.0000012'
  },
  {
    id: 5,
    timestamp: new Date(Date.now() - 310000).toISOString(),
    type: 'alert',
    message: 'Detected suspicious activity in MOON token',
    details: 'Large dev wallet selling, potential rug pull, blacklisting'
  },
  {
    id: 6,
    timestamp: new Date(Date.now() - 450000).toISOString(),
    type: 'scan',
    message: 'Running RugCheck.xyz verification',
    details: 'Checking 23 tokens from watchlist'
  },
  {
    id: 7,
    timestamp: new Date(Date.now() - 610000).toISOString(),
    type: 'analysis',
    message: 'Performing pattern recognition on DOGE',
    details: 'Identified double bottom pattern forming on 4h timeframe'
  },
  {
    id: 8,
    timestamp: new Date(Date.now() - 920000).toISOString(),
    type: 'decision',
    message: 'Calculated optimal entry for FLOKI',
    details: 'Based on Fibonacci retracement and volume profile'
  },
];

const AgentActivityMonitor = () => {
  const [activities, setActivities] = useState<ActivityLog[]>(mockActivities);
  const [newActivities, setNewActivities] = useState<ActivityLog[]>([]);
  const [activeFilter, setActiveFilter] = useState<string>('all');
  
  useEffect(() => {
    // Simulate new activities coming in
    const interval = setInterval(() => {
      const types = ['scan', 'analysis', 'decision', 'action', 'alert'];
      const type = types[Math.floor(Math.random() * types.length)] as ActivityLog['type'];
      
      const newActivity: ActivityLog = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type,
        message: `${type === 'scan' ? 'Scanning' : 
                  type === 'analysis' ? 'Analyzing' :
                  type === 'decision' ? 'Evaluating' :
                  type === 'action' ? 'Trading' :
                  'Alert for'} ${['BTC', 'ETH', 'DOGE', 'SHIB', 'PEPE'][Math.floor(Math.random() * 5)]}`,
        details: 'Simulated agent activity'
      };
      
      setNewActivities(prev => [newActivity, ...prev].slice(0, 5));
      setActivities(prev => [newActivity, ...prev].slice(0, 100));
    }, 8000);
    
    return () => clearInterval(interval);
  }, []);
  
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
