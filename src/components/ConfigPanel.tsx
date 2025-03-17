import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Settings, Bot, Network, Shield, Bell } from 'lucide-react';
import ApiConfigSection from './ApiConfigSection';

const ConfigPanel = () => {
  const [notifications, setNotifications] = useState({
    tradeAlerts: true,
    priceAlerts: true,
    newsAlerts: true,
    securityAlerts: true,
  });
  
  const [security, setSecurity] = useState({
    maxTradeAmount: "0.5",
    requireConfirmation: true,
    blacklistEnabled: true,
    emergencyStop: false,
  });
  
  return (
    <div className="glass-panel rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-border flex items-center">
        <Settings className="w-5 h-5 text-primary mr-2" />
        <h3 className="text-lg font-medium">Configuration</h3>
      </div>
      
      <div className="p-6">
        <Tabs defaultValue="api">
          <TabsList className="mb-6 grid grid-cols-4">
            <TabsTrigger value="api" className="flex items-center gap-1.5">
              <Network className="h-4 w-4" />
              <span>API</span>
            </TabsTrigger>
            <TabsTrigger value="agents" className="flex items-center gap-1.5">
              <Bot className="h-4 w-4" />
              <span>Agents</span>
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center gap-1.5">
              <Shield className="h-4 w-4" />
              <span>Security</span>
            </TabsTrigger>
            <TabsTrigger value="notifications" className="flex items-center gap-1.5">
              <Bell className="h-4 w-4" />
              <span>Notifications</span>
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="api">
            <ApiConfigSection />
          </TabsContent>
          
          <TabsContent value="agents">
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium mb-4">Agent Configuration</h3>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="agent-instructions">Global Agent Instructions</Label>
                    <textarea 
                      id="agent-instructions" 
                      className="w-full min-h-[100px] p-2 rounded-md border border-input bg-background"
                      placeholder="Enter global instructions for all agents..."
                    />
                    <p className="text-xs text-muted-foreground">
                      These instructions will be provided to all agents as part of their system prompt
                    </p>
                  </div>
                  
                  <Separator />
                  
                  <div className="space-y-3">
                    <Label>Active Agents</Label>
                    
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex flex-col">
                          <span className="font-medium">Market Analyst</span>
                          <span className="text-xs text-muted-foreground">Analyzes market data and news</span>
                        </div>
                        <Switch id="market-analyst" defaultChecked />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex flex-col">
                          <span className="font-medium">Trader</span>
                          <span className="text-xs text-muted-foreground">Executes trades based on signals</span>
                        </div>
                        <Switch id="trader" defaultChecked />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex flex-col">
                          <span className="font-medium">Learning Manager</span>
                          <span className="text-xs text-muted-foreground">Optimizes strategies based on outcomes</span>
                        </div>
                        <Switch id="learning-manager" defaultChecked />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex flex-col">
                          <span className="font-medium">Manager</span>
                          <span className="text-xs text-muted-foreground">Coordinates agent activities</span>
                        </div>
                        <Switch id="manager" defaultChecked />
                      </div>
                    </div>
                  </div>
                  
                  <Button className="w-full">Save Agent Configuration</Button>
                </div>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="security">
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium mb-4">Security Settings</h3>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="max-trade">Maximum Trade Amount (ETH)</Label>
                    <Input 
                      id="max-trade" 
                      type="number" 
                      placeholder="0.5" 
                      value={security.maxTradeAmount}
                      onChange={(e) => setSecurity({...security, maxTradeAmount: e.target.value})}
                    />
                    <p className="text-xs text-muted-foreground">
                      Maximum amount of ETH that can be used in a single trade
                    </p>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="confirm-trades">Require Trade Confirmation</Label>
                      <p className="text-xs text-muted-foreground">
                        Require manual confirmation before executing trades
                      </p>
                    </div>
                    <Switch 
                      id="confirm-trades" 
                      checked={security.requireConfirmation}
                      onCheckedChange={(checked) => setSecurity({...security, requireConfirmation: checked})}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="blacklist">Enable Token Blacklist</Label>
                      <p className="text-xs text-muted-foreground">
                        Automatically blacklist suspicious tokens
                      </p>
                    </div>
                    <Switch 
                      id="blacklist" 
                      checked={security.blacklistEnabled}
                      onCheckedChange={(checked) => setSecurity({...security, blacklistEnabled: checked})}
                    />
                  </div>
                  
                  <Separator />
                  
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="emergency-stop" className="text-destructive font-semibold">Emergency Stop</Label>
                      <p className="text-xs text-muted-foreground">
                        Immediately stop all trading activity
                      </p>
                    </div>
                    <Switch 
                      id="emergency-stop" 
                      checked={security.emergencyStop}
                      onCheckedChange={(checked) => setSecurity({...security, emergencyStop: checked})}
                    />
                  </div>
                  
                  <Button className="w-full">Save Security Settings</Button>
                </div>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="notifications">
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium mb-4">Notification Settings</h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="trade-alerts">Trade Alerts</Label>
                      <p className="text-xs text-muted-foreground">
                        Receive notifications for trade executions
                      </p>
                    </div>
                    <Switch 
                      id="trade-alerts" 
                      checked={notifications.tradeAlerts}
                      onCheckedChange={(checked) => setNotifications({...notifications, tradeAlerts: checked})}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="price-alerts">Price Alerts</Label>
                      <p className="text-xs text-muted-foreground">
                        Receive notifications for significant price movements
                      </p>
                    </div>
                    <Switch 
                      id="price-alerts" 
                      checked={notifications.priceAlerts}
                      onCheckedChange={(checked) => setNotifications({...notifications, priceAlerts: checked})}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="news-alerts">News Alerts</Label>
                      <p className="text-xs text-muted-foreground">
                        Receive notifications for important news
                      </p>
                    </div>
                    <Switch 
                      id="news-alerts" 
                      checked={notifications.newsAlerts}
                      onCheckedChange={(checked) => setNotifications({...notifications, newsAlerts: checked})}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="security-alerts">Security Alerts</Label>
                      <p className="text-xs text-muted-foreground">
                        Receive notifications for security issues
                      </p>
                    </div>
                    <Switch 
                      id="security-alerts" 
                      checked={notifications.securityAlerts}
                      onCheckedChange={(checked) => setNotifications({...notifications, securityAlerts: checked})}
                    />
                  </div>
                  
                  <Separator />
                  
                  <div className="space-y-2">
                    <Label htmlFor="telegram-bot-token">Telegram Bot Token (Optional)</Label>
                    <Input 
                      id="telegram-bot-token" 
                      type="password"
                      placeholder="Enter your Telegram bot token" 
                    />
                    <p className="text-xs text-muted-foreground">
                      For receiving notifications via Telegram
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="telegram-chat-id">Telegram Chat ID (Optional)</Label>
                    <Input 
                      id="telegram-chat-id" 
                      placeholder="Enter your Telegram chat ID" 
                    />
                    <p className="text-xs text-muted-foreground">
                      Your Telegram chat ID for receiving notifications
                    </p>
                  </div>
                  
                  <Button className="w-full">Save Notification Settings</Button>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ConfigPanel;
