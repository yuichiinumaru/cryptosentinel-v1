import { useState } from 'react';
import { AlertCircle, CheckCircle } from 'lucide-react';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface WalletOption {
  id: string;
  name: string;
  icon: React.ReactNode;
}

interface WalletConnectionProps {
  className?: string;
}

const WalletConnection = ({ className }: WalletConnectionProps) => {
  const [isConnected, setIsConnected] = useState(false);
  const [hasTrading, setHasTrading] = useState(false);
  const [isConnectedToCEX, setIsConnectedToCEX] = useState(false);
  const [selectedCEX, setSelectedCEX] = useState('Binance');

  const walletOptions: WalletOption[] = [
    { id: 'metamask', name: 'MetaMask', icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-wallet"><path d="M21 7.9V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-2.9"/><path d="M9 15V5"/><path d="M15 19v-4"/></svg> },
    { id: 'coinbase', name: 'Coinbase', icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-badge"><path d="M3.73 21a2 2 0 0 1 0-4.2"/><path d="M20.27 21a2 2 0 0 0 0-4.2"/><path d="M12 14a5 5 0 0 0-4.8-3.34"/><path d="M12 14a5 5 0 0 1 4.8-3.34"/><path d="M12 7a5 5 0 0 1 4.8 3.34"/><path d="M12 7a5 5 0 0 0-4.8 3.34"/><path d="M12 2a10 10 0 1 0 0 20"/><path d="M8.3 2.73a2 2 0 0 0-4.2 0"/><path d="M15.7 2.73a2 2 0 0 1 4.2 0"/></svg> },
  ];

  const cexOptions = ['Binance', 'Coinbase', 'Kraken'];

  const connectWallet = (wallet: WalletOption) => {
    setIsConnected(true);
    console.log(`Connecting to ${wallet.name}`);
  };

  const disconnectWallet = () => {
    setIsConnected(false);
    setIsConnectedToCEX(false);
    setHasTrading(false);
    console.log('Wallet disconnected');
  };

  const toggleCEXConnection = () => {
    setIsConnectedToCEX(prev => !prev);
  };

  return (
    <div className={cn("glass-panel rounded-lg", className)}>
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <h3 className="text-lg font-medium">Wallet Connection</h3>
        {isConnected && (
          <Button variant="destructive" size="sm" onClick={disconnectWallet}>
            Disconnect
          </Button>
        )}
      </div>
      
      <div className="p-4 space-y-4">
        {!isConnected ? (
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Connect your wallet to enable trading.
            </p>
            
            <div className="flex flex-wrap gap-2">
              {walletOptions.map((wallet) => (
                <Button
                  key={wallet.id}
                  variant="secondary"
                  className="flex-1"
                  onClick={() => connectWallet(wallet)}
                >
                  {wallet.icon}
                  {wallet.name}
                </Button>
              ))}
            </div>
            
            <div>
              <p className="text-sm font-medium">Or connect via CEX:</p>
              <select
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={selectedCEX}
                onChange={(e) => setSelectedCEX(e.target.value)}
              >
                {cexOptions.map((cex) => (
                  <option key={cex} value={cex}>
                    {cex}
                  </option>
                ))}
              </select>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Connected with MetaMask.
            </p>
            
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">Trading Permission:</p>
              <Switch 
                checked={hasTrading} 
                onCheckedChange={setHasTrading}
              />
            </div>
            
            <p className="text-xs text-muted-foreground">
              Granting trading permission allows the bot to execute trades on your behalf.
            </p>
            
            <Button
              variant="secondary"
              className={cn(
                "w-full",
                isConnectedToCEX ? "bg-success/10 text-success hover:bg-success/20" : ""
              )}
              onClick={toggleCEXConnection}
            >
              {isConnectedToCEX ? (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Connected to {selectedCEX}
                </>
              ) : (
                <>
                  <AlertCircle className="w-4 h-4 mr-2" />
                  Connect to {selectedCEX}
                </>
              )}
            </Button>
            
            <p className="text-xs text-muted-foreground">
              Connecting to a Centralized Exchange (CEX) allows for faster order execution.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default WalletConnection;
