
import { useState } from 'react';
import { LineChart, PieChart, CircleDollarSign, TrendingUp, TrendingDown, ArrowRightLeft, Activity } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useFadeIn } from '@/utils/animations';

// Mock data for tokens
const mockTokens = [
  { name: 'Ethereum', symbol: 'ETH', balance: 1.245, value: 3541.25, change: 2.4 },
  { name: 'Bitcoin', symbol: 'BTC', balance: 0.085, value: 4921.35, change: -1.2 },
  { name: 'Solana', symbol: 'SOL', balance: 45.5, value: 4370.0, change: 8.7 },
  { name: 'Uniswap', symbol: 'UNI', balance: 125.5, value: 625.5, change: -3.5 },
];

const FundsDashboard = () => {
  const fadeInStyle = useFadeIn(400);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Calculate total portfolio value
  const totalPortfolioValue = mockTokens.reduce((acc, token) => acc + token.value, 0);
  
  return (
    <div className="glass-panel rounded-lg" style={fadeInStyle}>
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CircleDollarSign className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-medium">Funds & Portfolio</h3>
        </div>
        <Button size="sm" variant="outline" className="gap-1.5">
          <ArrowRightLeft className="w-4 h-4" />
          Withdraw
        </Button>
      </div>

      <div className="p-4">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="tokens">Tokens</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="space-y-4">
            <div className="flex flex-col md:flex-row gap-4">
              <Card className="flex-1">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg flex justify-between">
                    <span>Portfolio Value</span>
                    <span className="text-lg">${totalPortfolioValue.toLocaleString()}</span>
                  </CardTitle>
                  <CardDescription className="flex items-center gap-1">
                    <TrendingUp className="w-4 h-4 text-success" />
                    <span className="text-success">+5.2% 24h</span>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[180px] flex items-center justify-center">
                    <div className="w-full h-full flex items-center justify-center">
                      <PieChart className="w-32 h-32 text-muted-foreground" />
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="flex-1">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">Performance</CardTitle>
                  <CardDescription>Last 7 days</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[180px] flex items-center justify-center">
                    <div className="w-full h-full flex items-center justify-center">
                      <LineChart className="w-full h-32 text-muted-foreground" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardHeader className="pb-2 pt-4">
                  <CardTitle className="text-sm text-muted-foreground">Active Positions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">7</div>
                  <div className="text-xs text-muted-foreground">4 profitable, 3 in loss</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2 pt-4">
                  <CardTitle className="text-sm text-muted-foreground">Monthly Profit</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-success">+$1,248.32</div>
                  <div className="text-xs text-muted-foreground">+12.3% from last month</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2 pt-4">
                  <CardTitle className="text-sm text-muted-foreground">AI Trading Efficiency</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">84%</div>
                  <div className="flex items-center gap-2 mt-1">
                    <Progress value={84} className="h-2" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          
          <TabsContent value="tokens">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h4 className="text-sm font-medium">Token Holdings</h4>
                <Button variant="outline" size="sm" className="text-xs h-8">
                  <ArrowRightLeft className="mr-1 h-3 w-3" /> Swap
                </Button>
              </div>
              
              <div className="bg-card rounded-lg border border-border overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-muted/50">
                        <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Asset</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">Balance</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">Value</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">Change (24h)</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mockTokens.map((token, index) => (
                        <tr key={index} className="border-t border-border">
                          <td className="px-4 py-3 text-sm">
                            <div className="flex items-center">
                              <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center mr-2">
                                {token.symbol.substring(0, 1)}
                              </div>
                              <div>
                                <div className="font-medium">{token.name}</div>
                                <div className="text-xs text-muted-foreground">{token.symbol}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-sm text-right">{token.balance}</td>
                          <td className="px-4 py-3 text-sm text-right">${token.value.toLocaleString()}</td>
                          <td className="px-4 py-3 text-sm text-right">
                            <span className={token.change >= 0 ? 'text-success' : 'text-destructive'}>
                              {token.change >= 0 ? '+' : ''}{token.change}%
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm text-right">
                            <div className="flex justify-end space-x-2">
                              <Button variant="ghost" size="sm" className="h-8 px-2">Buy</Button>
                              <Button variant="ghost" size="sm" className="h-8 px-2">Sell</Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="performance">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h4 className="text-sm font-medium">Trading Performance</h4>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" className="text-xs h-8">1D</Button>
                  <Button variant="default" size="sm" className="text-xs h-8">1W</Button>
                  <Button variant="outline" size="sm" className="text-xs h-8">1M</Button>
                  <Button variant="outline" size="sm" className="text-xs h-8">1Y</Button>
                </div>
              </div>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-card p-4 rounded-lg border border-border">
                  <div className="text-xs text-muted-foreground mb-1">Total Trades</div>
                  <div className="text-2xl font-bold">127</div>
                  <div className="flex items-center text-xs mt-1">
                    <Activity className="h-3 w-3 mr-1" />
                    <span>15 active</span>
                  </div>
                </div>
                
                <div className="bg-card p-4 rounded-lg border border-border">
                  <div className="text-xs text-muted-foreground mb-1">Win Rate</div>
                  <div className="text-2xl font-bold">72%</div>
                  <div className="flex items-center text-xs mt-1">
                    <TrendingUp className="h-3 w-3 mr-1 text-success" />
                    <span className="text-success">+4% from last week</span>
                  </div>
                </div>
                
                <div className="bg-card p-4 rounded-lg border border-border">
                  <div className="text-xs text-muted-foreground mb-1">Profit Factor</div>
                  <div className="text-2xl font-bold">2.36</div>
                  <div className="flex items-center text-xs mt-1">
                    <TrendingUp className="h-3 w-3 mr-1 text-success" />
                    <span className="text-success">Good risk-reward ratio</span>
                  </div>
                </div>
                
                <div className="bg-card p-4 rounded-lg border border-border">
                  <div className="text-xs text-muted-foreground mb-1">Maximum Drawdown</div>
                  <div className="text-2xl font-bold">-8.2%</div>
                  <div className="flex items-center text-xs mt-1">
                    <TrendingDown className="h-3 w-3 mr-1 text-destructive" />
                    <span>Within risk parameters</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-card rounded-lg border border-border p-4 h-64 flex items-center justify-center">
                <LineChart className="w-full h-full text-muted-foreground" />
              </div>
              
              <div className="bg-card rounded-lg border border-border overflow-hidden">
                <div className="px-4 py-3 border-b border-border">
                  <h4 className="text-sm font-medium">Recent Trades</h4>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-muted/50">
                        <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Token</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Type</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">Amount</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">Price</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">P/L</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-t border-border">
                        <td className="px-4 py-3 text-sm">
                          <div className="flex items-center">
                            <Badge variant="outline" className="mr-2">ETH</Badge>
                            <span>Ethereum</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <Badge variant="success">BUY</Badge>
                        </td>
                        <td className="px-4 py-3 text-sm text-right">0.5 ETH</td>
                        <td className="px-4 py-3 text-sm text-right">$2,845.20</td>
                        <td className="px-4 py-3 text-sm text-right text-success">+$142.26</td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">Today, 10:45 AM</td>
                      </tr>
                      <tr className="border-t border-border">
                        <td className="px-4 py-3 text-sm">
                          <div className="flex items-center">
                            <Badge variant="outline" className="mr-2">SOL</Badge>
                            <span>Solana</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <Badge variant="destructive">SELL</Badge>
                        </td>
                        <td className="px-4 py-3 text-sm text-right">10 SOL</td>
                        <td className="px-4 py-3 text-sm text-right">$95.34</td>
                        <td className="px-4 py-3 text-sm text-right text-destructive">-$28.50</td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">Yesterday, 3:22 PM</td>
                      </tr>
                      <tr className="border-t border-border">
                        <td className="px-4 py-3 text-sm">
                          <div className="flex items-center">
                            <Badge variant="outline" className="mr-2">UNI</Badge>
                            <span>Uniswap</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <Badge variant="success">BUY</Badge>
                        </td>
                        <td className="px-4 py-3 text-sm text-right">50 UNI</td>
                        <td className="px-4 py-3 text-sm text-right">$5.20</td>
                        <td className="px-4 py-3 text-sm text-right text-success">+$72.80</td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">Jun 15, 9:10 AM</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default FundsDashboard;
