
import { useState } from 'react';
import { Wallet, ArrowRight, Check, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';

const WalletConnection = () => {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('dex');
  const [walletAddress, setWalletAddress] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isAllowingTrading, setIsAllowingTrading] = useState(false);
  const [connectedWallet, setConnectedWallet] = useState('');
  const [cexApiKey, setCexApiKey] = useState('');
  const [cexApiSecret, setCexApiSecret] = useState('');
  const [selectedDex, setSelectedDex] = useState('uniswap');
  const [selectedCex, setSelectedCex] = useState('binance');
  const [maxTradingAmount, setMaxTradingAmount] = useState('0.5');

  const handleConnectWallet = () => {
    // Simulate wallet connection
    if (activeTab === 'dex') {
      if (walletAddress.length >= 40) {
        setIsConnected(true);
        setConnectedWallet(walletAddress);
        toast({
          title: "Wallet Connected",
          description: `Successfully connected to ${walletAddress.substring(0, 6)}...${walletAddress.substring(walletAddress.length - 4)}`,
        });
      } else {
        toast({
          title: "Invalid Wallet Address",
          description: "Please enter a valid wallet address",
          variant: "destructive",
        });
      }
    } else if (activeTab === 'cex') {
      if (cexApiKey.length > 5 && cexApiSecret.length > 5) {
        setIsConnected(true);
        toast({
          title: "Exchange Connected",
          description: `Successfully connected to ${selectedCex}`,
        });
      } else {
        toast({
          title: "Invalid API Keys",
          description: "Please enter valid API keys",
          variant: "destructive",
        });
      }
    }
  };

  const handleDisconnect = () => {
    setIsConnected(false);
    setIsAllowingTrading(false);
    setConnectedWallet('');
    toast({
      title: "Disconnected",
      description: activeTab === 'dex' ? "Wallet disconnected" : "Exchange disconnected",
    });
  };

  return (
    <div className="glass-panel rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Wallet className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-medium">Trading Connection</h3>
        </div>
        {isConnected && (
          <Badge variant={isAllowingTrading ? "success" : "secondary"}>
            {isAllowingTrading ? "Trading Enabled" : "Connected"}
          </Badge>
        )}
      </div>
      
      <div className="p-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid grid-cols-2 mb-4">
            <TabsTrigger value="dex" className="flex items-center gap-1.5">
              <ArrowRight className="w-4 h-4" />
              <span>DEX Wallet</span>
            </TabsTrigger>
            <TabsTrigger value="cex" className="flex items-center gap-1.5">
              <ArrowRight className="w-4 h-4" />
              <span>CEX Exchange</span>
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="dex" className="space-y-4">
            {!isConnected ? (
              <>
                <div className="mb-4">
                  <Label htmlFor="dex-select" className="mb-1 block">Select DEX</Label>
                  <select 
                    id="dex-select"
                    value={selectedDex}
                    onChange={(e) => setSelectedDex(e.target.value)}
                    className="w-full px-3 py-2 border border-input rounded-md"
                  >
                    <option value="uniswap">Uniswap V3 (Ethereum)</option>
                    <option value="pancakeswap">PancakeSwap (BNB Chain)</option>
                    <option value="sushiswap">SushiSwap (Multi-chain)</option>
                    <option value="baseswap">BaseSwap (Base)</option>
                  </select>
                </div>
                
                <div className="mb-4">
                  <Label htmlFor="wallet-address" className="mb-1 block">Wallet Address</Label>
                  <Input
                    id="wallet-address"
                    placeholder="0x..."
                    value={walletAddress}
                    onChange={(e) => setWalletAddress(e.target.value)}
                  />
                </div>
                
                <Button onClick={handleConnectWallet} className="w-full">
                  Connect Wallet
                </Button>
              </>
            ) : (
              <div className="space-y-4">
                <div className="p-3 bg-success/10 border border-success/20 rounded-md flex items-start gap-2">
                  <Check className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Wallet Connected</p>
                    <p className="text-xs text-muted-foreground font-mono mt-1">
                      {connectedWallet.substring(0, 6)}...{connectedWallet.substring(connectedWallet.length - 4)}
                    </p>
                    <p className="text-xs mt-2">
                      Connected to: <Badge variant="outline" className="font-normal">{selectedDex}</Badge>
                    </p>
                  </div>
                </div>
                
                <div className="flex flex-col space-y-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-sm font-medium">Enable AI Trading</p>
                      <p className="text-xs text-muted-foreground">Allow AI agent to execute trades</p>
                    </div>
                    <Switch 
                      checked={isAllowingTrading} 
                      onCheckedChange={setIsAllowingTrading}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="max-amount" className="mb-1 block">Maximum Trading Amount (ETH)</Label>
                    <Input
                      id="max-amount"
                      type="number"
                      value={maxTradingAmount}
                      onChange={(e) => setMaxTradingAmount(e.target.value)}
                      min={0.01}
                      max={10}
                      step={0.01}
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      AI agent won't spend more than this amount per trade
                    </p>
                  </div>
                  
                  <div className="p-3 bg-warning/10 border border-warning/20 rounded-md flex items-start gap-2">
                    <AlertCircle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">Security Notice</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Never share your private keys. This integration uses read-only wallet connections 
                        and requires manual transaction approval through your wallet.
                      </p>
                    </div>
                  </div>
                  
                  <Button onClick={handleDisconnect} variant="outline" className="w-full">
                    Disconnect Wallet
                  </Button>
                </div>
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="cex" className="space-y-4">
            {!isConnected ? (
              <>
                <div className="mb-4">
                  <Label htmlFor="cex-select" className="mb-1 block">Select Exchange</Label>
                  <select 
                    id="cex-select"
                    value={selectedCex}
                    onChange={(e) => setSelectedCex(e.target.value)}
                    className="w-full px-3 py-2 border border-input rounded-md"
                  >
                    <option value="binance">Binance</option>
                    <option value="kucoin">KuCoin</option>
                    <option value="coinbase">Coinbase</option>
                    <option value="okx">OKX</option>
                  </select>
                </div>
                
                <div className="mb-4">
                  <Label htmlFor="api-key" className="mb-1 block">API Key</Label>
                  <Input
                    id="api-key"
                    type="text"
                    value={cexApiKey}
                    onChange={(e) => setCexApiKey(e.target.value)}
                    placeholder="Enter your API key"
                  />
                </div>
                
                <div className="mb-4">
                  <Label htmlFor="api-secret" className="mb-1 block">API Secret</Label>
                  <Input
                    id="api-secret"
                    type="password"
                    value={cexApiSecret}
                    onChange={(e) => setCexApiSecret(e.target.value)}
                    placeholder="Enter your API secret"
                  />
                </div>
                
                <Button onClick={handleConnectWallet} className="w-full">
                  Connect Exchange
                </Button>
              </>
            ) : (
              <div className="space-y-4">
                <div className="p-3 bg-success/10 border border-success/20 rounded-md flex items-start gap-2">
                  <Check className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Exchange Connected</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Successfully connected to {selectedCex}
                    </p>
                  </div>
                </div>
                
                <div className="flex flex-col space-y-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-sm font-medium">Enable AI Trading</p>
                      <p className="text-xs text-muted-foreground">Allow AI agent to execute trades</p>
                    </div>
                    <Switch 
                      checked={isAllowingTrading} 
                      onCheckedChange={setIsAllowingTrading}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="max-amount-cex" className="mb-1 block">Maximum Trading Amount (USD)</Label>
                    <Input
                      id="max-amount-cex"
                      type="number"
                      value={maxTradingAmount}
                      onChange={(e) => setMaxTradingAmount(e.target.value)}
                      min={10}
                      max={10000}
                      step={10}
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      AI agent won't spend more than this amount per trade
                    </p>
                  </div>
                  
                  <div className="p-3 bg-warning/10 border border-warning/20 rounded-md flex items-start gap-2">
                    <AlertCircle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">Security Notice</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        For security, create API keys with trading permissions only.
                        Disable withdrawals and other sensitive operations in the exchange settings.
                      </p>
                    </div>
                  </div>
                  
                  <Button onClick={handleDisconnect} variant="outline" className="w-full">
                    Disconnect Exchange
                  </Button>
                </div>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default WalletConnection;
