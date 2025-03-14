import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Wallet, ArrowUpRight, ArrowDownRight, DollarSign, CreditCard, RefreshCw, ShieldCheck, History } from 'lucide-react';

const FundsDashboard = () => {
  const [activeTab, setActiveTab] = useState('wallets');
  
  return (
    <div className="glass-panel rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-medium">Funds Dashboard</h3>
        </div>
      </div>
      
      <div className="p-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Total Balance</CardTitle>
              <CardDescription>Across all wallets</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">$24,894.32</div>
              <div className="flex items-center text-sm text-muted-foreground mt-1">
                <Badge variant="outline" className="bg-green-500/10 text-green-500 hover:bg-green-500/20 border-0">
                  <ArrowUpRight className="mr-1 h-3 w-3" />
                  +5.2%
                </Badge>
                <span className="ml-2">24h change</span>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Hot Wallet</CardTitle>
              <CardDescription>Trading funds</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">$7,325.18</div>
              <div className="flex items-center text-sm text-muted-foreground mt-1">
                <Badge variant="outline" className="bg-red-500/10 text-red-500 hover:bg-red-500/20 border-0">
                  <ArrowDownRight className="mr-1 h-3 w-3" />
                  -1.8%
                </Badge>
                <span className="ml-2">24h change</span>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Cold Storage</CardTitle>
              <CardDescription>Long-term funds</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">$17,569.14</div>
              <div className="flex items-center text-sm text-muted-foreground mt-1">
                <Badge variant="outline" className="bg-green-500/10 text-green-500 hover:bg-green-500/20 border-0">
                  <ArrowUpRight className="mr-1 h-3 w-3" />
                  +8.4%
                </Badge>
                <span className="ml-2">24h change</span>
              </div>
            </CardContent>
          </Card>
        </div>
        
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-3 mb-4">
            <TabsTrigger value="wallets">Wallets</TabsTrigger>
            <TabsTrigger value="transactions">Transactions</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
          </TabsList>
          
          <TabsContent value="wallets" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <Wallet className="mr-2 h-5 w-5" />
                  Hot Wallet
                </CardTitle>
                <CardDescription>
                  Used for active trading operations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Wallet Address:</span>
                    <span className="font-mono">0x7F5a...3E21</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Network:</span>
                    <span>Ethereum Mainnet</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">ETH Balance:</span>
                    <span>2.45 ETH</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">USDT Balance:</span>
                    <span>2,420.65 USDT</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Status:</span>
                    <Badge variant="secondary" className="bg-green-500/10 text-green-500 hover:bg-green-500/20 border-0">
                      Active
                    </Badge>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button variant="outline" size="sm">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh
                </Button>
                <Button size="sm">
                  <CreditCard className="mr-2 h-4 w-4" />
                  Manage
                </Button>
              </CardFooter>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <ShieldCheck className="mr-2 h-5 w-5" />
                  Cold Storage
                </CardTitle>
                <CardDescription>
                  Secure long-term storage
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Wallet Address:</span>
                    <span className="font-mono">0x9E2c...7F11</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Network:</span>
                    <span>Ethereum Mainnet</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">ETH Balance:</span>
                    <span>5.89 ETH</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">USDT Balance:</span>
                    <span>5,124.37 USDT</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Status:</span>
                    <Badge variant="secondary" className="bg-green-500/10 text-green-500 hover:bg-green-500/20 border-0">
                      Secured
                    </Badge>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button variant="outline" size="sm">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh
                </Button>
                <Button size="sm">
                  <CreditCard className="mr-2 h-4 w-4" />
                  Manage
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>
          
          <TabsContent value="transactions" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <History className="mr-2 h-5 w-5" />
                  Recent Transactions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Transaction items would go here */}
                  <div className="text-muted-foreground text-center py-6">
                    Transaction history will appear here
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="security" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <ShieldCheck className="mr-2 h-5 w-5" />
                  Security Settings
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Security settings would go here */}
                  <div className="text-muted-foreground text-center py-6">
                    Security settings will appear here
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default FundsDashboard;
