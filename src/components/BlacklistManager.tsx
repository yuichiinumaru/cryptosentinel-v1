
import { useState } from 'react';
import { X, Search, AlertTriangle, User, Coins } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import { useToast } from '@/components/ui/use-toast';

interface BlacklistItem {
  id: string;
  address: string;
  name?: string;
  reason: string;
  timestamp: Date;
  source: 'user' | 'auto' | 'community';
}

const BlacklistManager = () => {
  const [activeTab, setActiveTab] = useState('tokens');
  const [searchTerm, setSearchTerm] = useState('');
  const { toast } = useToast();
  
  const [tokenBlacklist, setTokenBlacklist] = useState<BlacklistItem[]>([
    {
      id: 'token-1',
      address: '0x7af3d24f1cc9bec59cdc153a0a59a8981584fe3b',
      name: 'SafeMoon Fork',
      reason: 'Rug pull detected by algorithm',
      timestamp: new Date(Date.now() - 86400000 * 2),
      source: 'auto'
    },
    {
      id: 'token-2',
      address: '0x65a8157823d3e2195c9bb0851f74fb5c6f8f3cb2',
      name: 'ELONDOG',
      reason: 'Bundled coin supply, liquidity pulled after 2hrs',
      timestamp: new Date(Date.now() - 86400000 * 5),
      source: 'community'
    },
    {
      id: 'token-3',
      address: '0x9dc433dbce70946456d9a3fa3ce93bf7fbed685c',
      name: 'TrustWallet Clone',
      reason: 'Honeypot contract, users unable to sell',
      timestamp: new Date(Date.now() - 86400000 * 1),
      source: 'auto'
    }
  ]);
  
  const [devBlacklist, setDevBlacklist] = useState<BlacklistItem[]>([
    {
      id: 'dev-1',
      address: '0x61bf2f45b130a6b4f88cc07ff2c118eac789a31b',
      name: 'RugDev1',
      reason: 'Multiple rug pulls confirmed',
      timestamp: new Date(Date.now() - 86400000 * 10),
      source: 'auto'
    },
    {
      id: 'dev-2',
      address: '0xfba8c1b55a58ed8eefb56e2b50c1d5fad7204d2c',
      name: 'UnknownDev',
      reason: 'Linked to 3 honeypot contracts',
      timestamp: new Date(Date.now() - 86400000 * 3),
      source: 'community'
    }
  ]);
  
  const [newAddress, setNewAddress] = useState('');
  const [newReason, setNewReason] = useState('');
  
  const handleAddToBlacklist = () => {
    if (!newAddress) {
      toast({
        title: "Error",
        description: "Please enter an address",
        variant: "destructive"
      });
      return;
    }
    
    const newItem: BlacklistItem = {
      id: `${activeTab}-${Date.now()}`,
      address: newAddress,
      reason: newReason || 'Manually blacklisted',
      timestamp: new Date(),
      source: 'user'
    };
    
    if (activeTab === 'tokens') {
      setTokenBlacklist(prev => [newItem, ...prev]);
    } else {
      setDevBlacklist(prev => [newItem, ...prev]);
    }
    
    toast({
      title: "Added to blacklist",
      description: `Address has been added to the ${activeTab} blacklist.`
    });
    
    setNewAddress('');
    setNewReason('');
  };
  
  const handleRemoveItem = (id: string) => {
    if (activeTab === 'tokens') {
      setTokenBlacklist(prev => prev.filter(item => item.id !== id));
    } else {
      setDevBlacklist(prev => prev.filter(item => item.id !== id));
    }
    
    toast({
      title: "Removed from blacklist",
      description: "Address has been removed from the blacklist."
    });
  };
  
  const currentBlacklist = activeTab === 'tokens' ? tokenBlacklist : devBlacklist;
  const filteredBlacklist = currentBlacklist.filter(item => 
    item.address.toLowerCase().includes(searchTerm.toLowerCase()) || 
    (item.name && item.name.toLowerCase().includes(searchTerm.toLowerCase()))
  );
  
  return (
    <div className="glass-panel rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-border">
        <h3 className="text-lg font-medium">Blacklist Manager</h3>
      </div>
      
      <Tabs defaultValue="tokens" value={activeTab} onValueChange={setActiveTab}>
        <div className="px-4 pt-4">
          <TabsList className="grid grid-cols-2 mb-4">
            <TabsTrigger value="tokens" className="flex items-center gap-2">
              <Coins className="w-4 h-4" />
              <span>Tokens</span>
            </TabsTrigger>
            <TabsTrigger value="developers" className="flex items-center gap-2">
              <User className="w-4 h-4" />
              <span>Developers</span>
            </TabsTrigger>
          </TabsList>
          
          <div className="flex gap-3 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search blacklist..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>
          
          <div className="mb-4 p-4 bg-muted/50 rounded-lg border border-border">
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1">
                <Input
                  placeholder={`Add ${activeTab === 'tokens' ? 'token' : 'developer'} address...`}
                  value={newAddress}
                  onChange={(e) => setNewAddress(e.target.value)}
                />
              </div>
              <div className="flex-1">
                <Input
                  placeholder="Reason for blacklisting..."
                  value={newReason}
                  onChange={(e) => setNewReason(e.target.value)}
                />
              </div>
              <Button onClick={handleAddToBlacklist}>
                Add to Blacklist
              </Button>
            </div>
          </div>
        </div>
        
        <TabsContent value="tokens" className="p-0 m-0">
          <BlacklistDisplay 
            items={filteredBlacklist} 
            onRemove={handleRemoveItem}
            emptyMessage="No tokens in blacklist"
            type="token"
          />
        </TabsContent>
        
        <TabsContent value="developers" className="p-0 m-0">
          <BlacklistDisplay 
            items={filteredBlacklist} 
            onRemove={handleRemoveItem}
            emptyMessage="No developers in blacklist"
            type="developer"
          />
        </TabsContent>
      </Tabs>
    </div>
  );
};

interface BlacklistDisplayProps {
  items: BlacklistItem[];
  onRemove: (id: string) => void;
  emptyMessage: string;
  type: 'token' | 'developer';
}

const BlacklistDisplay = ({ items, onRemove, emptyMessage, type }: BlacklistDisplayProps) => {
  if (items.length === 0) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        {emptyMessage}
      </div>
    );
  }
  
  return (
    <div className="max-h-[400px] overflow-y-auto subtle-scroll">
      <div className="divide-y divide-border">
        {items.map(item => (
          <div key={item.id} className="p-4 hover:bg-secondary/30 transition-colors">
            <div className="flex justify-between items-start">
              <div>
                <div className="flex items-center gap-2">
                  {item.name && (
                    <span className="font-medium">{item.name}</span>
                  )}
                  <span className={cn(
                    "badge text-xs",
                    item.source === 'auto' ? 'badge-info' : 
                    item.source === 'community' ? 'badge-warning' : 'badge-success'
                  )}>
                    {item.source === 'auto' ? 'AI Detection' : 
                     item.source === 'community' ? 'Community Report' : 'Manual Entry'}
                  </span>
                </div>
                <div className="text-sm font-mono mt-1 text-muted-foreground">
                  {item.address.substring(0, 8)}...{item.address.substring(item.address.length - 6)}
                </div>
                <div className="mt-2 flex items-start gap-1">
                  <AlertTriangle className="w-4 h-4 text-warning mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{item.reason}</span>
                </div>
                <div className="mt-1 text-xs text-muted-foreground">
                  Added {item.timestamp.toLocaleDateString()} at {item.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </div>
              </div>
              
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={() => onRemove(item.id)}
                className="text-muted-foreground hover:text-destructive"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BlacklistManager;
