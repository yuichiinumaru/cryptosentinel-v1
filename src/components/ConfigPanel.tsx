
import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Settings, RefreshCw, Brain, 
  LineChart, Shield, Network, Save
} from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { cn } from '@/lib/utils';

interface ConfigSectionProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}

const ConfigSection = ({ title, description, icon, children }: ConfigSectionProps) => (
  <div className="mb-8">
    <div className="flex items-center gap-2 mb-2">
      <div className="p-1.5 rounded-full bg-primary/10 text-primary">
        {icon}
      </div>
      <h3 className="text-lg font-medium">{title}</h3>
    </div>
    <p className="text-muted-foreground mb-4">{description}</p>
    <div className="space-y-4">{children}</div>
  </div>
);

interface SettingItemProps {
  label: string;
  description?: string;
  children: React.ReactNode;
}

const SettingItem = ({ label, description, children }: SettingItemProps) => (
  <div className="flex flex-col sm:flex-row sm:items-center justify-between py-3 gap-3">
    <div>
      <Label className="text-sm font-medium">{label}</Label>
      {description && (
        <p className="text-xs text-muted-foreground">{description}</p>
      )}
    </div>
    <div className="flex items-center">
      {children}
    </div>
  </div>
);

const ConfigPanel = () => {
  const { toast } = useToast();
  
  const [settings, setSettings] = useState({
    // Trading settings
    autoTrading: true,
    maxTransactionsPerDay: 50,
    maxAmountPerTrade: 0.5,
    stopLossPercentage: 15,
    takeProfitPercentage: 25,
    slippageTolerance: 2,
    
    // Risk settings
    riskLevel: 2, // 1-low, 2-medium, 3-high
    enableRugCheckIntegration: true,
    enablePocketUniverseAPI: true,
    analyzeLiquidityDepth: true,
    contractAgeMinDays: 2,
    minLiquidityUSD: 50000,
    
    // AI settings
    sentimentAnalysisWeight: 25,
    technicalAnalysisWeight: 50,
    fundamentalAnalysisWeight: 25,
    refreshInterval: 15, // minutes
    detectionSensitivity: 70,
    
    // API keys
    rugCheckApiKey: '',
    pocketUniverseApiKey: '',
    dexScreenerApiKey: ''
  });

  const handleSwitchChange = (key: string) => (checked: boolean) => {
    setSettings(prev => ({ ...prev, [key]: checked }));
  };

  const handleSliderChange = (key: string) => (value: number[]) => {
    setSettings(prev => ({ ...prev, [key]: value[0] }));
  };

  const handleInputChange = (key: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.type === 'number' ? parseFloat(e.target.value) : e.target.value;
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSaveConfig = () => {
    toast({
      title: "Configuration Saved",
      description: "Your trading bot configuration has been updated."
    });
  };

  return (
    <div className="glass-panel rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <h3 className="text-lg font-medium">Trading Bot Configuration</h3>
        <Button 
          onClick={handleSaveConfig}
          size="sm"
          className="gap-1.5"
        >
          <Save className="w-4 h-4" /> 
          Save
        </Button>
      </div>
      
      <div className="p-6">
        <Tabs defaultValue="trading">
          <TabsList className="grid grid-cols-4 mb-6">
            <TabsTrigger value="trading" className="flex items-center gap-1.5 text-xs sm:text-sm">
              <Settings className="w-4 h-4" />
              <span className="hidden sm:inline">Trading</span>
            </TabsTrigger>
            <TabsTrigger value="risk" className="flex items-center gap-1.5 text-xs sm:text-sm">
              <Shield className="w-4 h-4" />
              <span className="hidden sm:inline">Risk</span>
            </TabsTrigger>
            <TabsTrigger value="ai" className="flex items-center gap-1.5 text-xs sm:text-sm">
              <Brain className="w-4 h-4" />
              <span className="hidden sm:inline">AI</span>
            </TabsTrigger>
            <TabsTrigger value="api" className="flex items-center gap-1.5 text-xs sm:text-sm">
              <Network className="w-4 h-4" />
              <span className="hidden sm:inline">APIs</span>
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="trading">
            <ConfigSection
              title="Trading Parameters"
              description="Configure how the bot executes trades and manages positions"
              icon={<Settings className="w-4 h-4" />}
            >
              <SettingItem 
                label="Automatic Trading" 
                description="Allow bot to execute trades without manual confirmation"
              >
                <Switch 
                  checked={settings.autoTrading} 
                  onCheckedChange={handleSwitchChange('autoTrading')}
                />
              </SettingItem>
              
              <SettingItem 
                label="Maximum Daily Transactions" 
                description="Limit the number of trades per 24hr period"
              >
                <div className="w-48">
                  <Slider 
                    value={[settings.maxTransactionsPerDay]} 
                    onValueChange={handleSliderChange('maxTransactionsPerDay')}
                    min={5}
                    max={200}
                    step={5}
                  />
                  <div className="text-center mt-2 text-sm">
                    {settings.maxTransactionsPerDay} trades
                  </div>
                </div>
              </SettingItem>
              
              <SettingItem 
                label="Maximum Amount Per Trade" 
                description="Maximum ETH to use per transaction"
              >
                <Input
                  type="number"
                  value={settings.maxAmountPerTrade}
                  onChange={handleInputChange('maxAmountPerTrade')}
                  min={0.01}
                  max={10}
                  step={0.01}
                  className="w-24"
                />
              </SettingItem>
              
              <SettingItem 
                label="Stop Loss" 
                description="Automatic sell when loss exceeds threshold"
              >
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    value={settings.stopLossPercentage}
                    onChange={handleInputChange('stopLossPercentage')}
                    min={1}
                    max={50}
                    className="w-20"
                  />
                  <span>%</span>
                </div>
              </SettingItem>
              
              <SettingItem 
                label="Take Profit" 
                description="Automatic sell when profit reaches threshold"
              >
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    value={settings.takeProfitPercentage}
                    onChange={handleInputChange('takeProfitPercentage')}
                    min={1}
                    max={500}
                    className="w-20"
                  />
                  <span>%</span>
                </div>
              </SettingItem>
              
              <SettingItem 
                label="Slippage Tolerance" 
                description="Maximum price difference tolerance"
              >
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    value={settings.slippageTolerance}
                    onChange={handleInputChange('slippageTolerance')}
                    min={0.1}
                    max={10}
                    step={0.1}
                    className="w-20"
                  />
                  <span>%</span>
                </div>
              </SettingItem>
            </ConfigSection>
          </TabsContent>
          
          <TabsContent value="risk">
            <ConfigSection
              title="Risk Management"
              description="Protect your assets with advanced risk detection"
              icon={<Shield className="w-4 h-4" />}
            >
              <SettingItem 
                label="Risk Level" 
                description="Overall risk tolerance for the bot"
              >
                <div className="space-x-2">
                  <Button 
                    size="sm" 
                    variant={settings.riskLevel === 1 ? "default" : "outline"}
                    onClick={() => setSettings(prev => ({ ...prev, riskLevel: 1 }))}
                  >
                    Low
                  </Button>
                  <Button 
                    size="sm" 
                    variant={settings.riskLevel === 2 ? "default" : "outline"}
                    onClick={() => setSettings(prev => ({ ...prev, riskLevel: 2 }))}
                  >
                    Medium
                  </Button>
                  <Button 
                    size="sm" 
                    variant={settings.riskLevel === 3 ? "default" : "outline"}
                    onClick={() => setSettings(prev => ({ ...prev, riskLevel: 3 }))}
                  >
                    High
                  </Button>
                </div>
              </SettingItem>
              
              <SettingItem 
                label="RugCheck.xyz Integration" 
                description="Verify contract safety with RugCheck"
              >
                <Switch 
                  checked={settings.enableRugCheckIntegration} 
                  onCheckedChange={handleSwitchChange('enableRugCheckIntegration')}
                />
              </SettingItem>
              
              <SettingItem 
                label="Pocket Universe API" 
                description="Use Pocket Universe for additional verification"
              >
                <Switch 
                  checked={settings.enablePocketUniverseAPI} 
                  onCheckedChange={handleSwitchChange('enablePocketUniverseAPI')}
                />
              </SettingItem>
              
              <SettingItem 
                label="Analyze Liquidity Depth" 
                description="Check for fake liquidity and volume"
              >
                <Switch 
                  checked={settings.analyzeLiquidityDepth} 
                  onCheckedChange={handleSwitchChange('analyzeLiquidityDepth')}
                />
              </SettingItem>
              
              <SettingItem 
                label="Minimum Contract Age" 
                description="Only trade tokens older than specified days"
              >
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    value={settings.contractAgeMinDays}
                    onChange={handleInputChange('contractAgeMinDays')}
                    min={0}
                    max={30}
                    className="w-20"
                  />
                  <span>days</span>
                </div>
              </SettingItem>
              
              <SettingItem 
                label="Minimum Liquidity" 
                description="Only trade tokens with sufficient liquidity"
              >
                <div className="flex items-center gap-2">
                  <span>$</span>
                  <Input
                    type="number"
                    value={settings.minLiquidityUSD}
                    onChange={handleInputChange('minLiquidityUSD')}
                    min={1000}
                    max={1000000}
                    step={1000}
                    className="w-32"
                  />
                </div>
              </SettingItem>
            </ConfigSection>
          </TabsContent>
          
          <TabsContent value="ai">
            <ConfigSection
              title="AI Configuration"
              description="Adjust the AI agent parameters and analysis weights"
              icon={<Brain className="w-4 h-4" />}
            >
              <div className="space-y-6">
                <div>
                  <Label className="mb-1 block">Analysis Weighting</Label>
                  <p className="text-xs text-muted-foreground mb-4">
                    Adjust how much influence each analysis type has on trading decisions
                  </p>
                  
                  <div className="space-y-5">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm">Sentiment Analysis</span>
                        <span className="text-sm">{settings.sentimentAnalysisWeight}%</span>
                      </div>
                      <Slider 
                        value={[settings.sentimentAnalysisWeight]} 
                        onValueChange={handleSliderChange('sentimentAnalysisWeight')}
                        min={0}
                        max={100}
                        step={5}
                      />
                    </div>
                    
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm">Technical Analysis</span>
                        <span className="text-sm">{settings.technicalAnalysisWeight}%</span>
                      </div>
                      <Slider 
                        value={[settings.technicalAnalysisWeight]} 
                        onValueChange={handleSliderChange('technicalAnalysisWeight')}
                        min={0}
                        max={100}
                        step={5}
                      />
                    </div>
                    
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm">Fundamental Analysis</span>
                        <span className="text-sm">{settings.fundamentalAnalysisWeight}%</span>
                      </div>
                      <Slider 
                        value={[settings.fundamentalAnalysisWeight]} 
                        onValueChange={handleSliderChange('fundamentalAnalysisWeight')}
                        min={0}
                        max={100}
                        step={5}
                      />
                    </div>
                  </div>
                </div>
                
                <SettingItem 
                  label="Data Refresh Interval" 
                  description="How often the AI updates its market analysis"
                >
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      value={settings.refreshInterval}
                      onChange={handleInputChange('refreshInterval')}
                      min={1}
                      max={60}
                      className="w-20"
                    />
                    <span>minutes</span>
                  </div>
                </SettingItem>
                
                <SettingItem 
                  label="Rug Detection Sensitivity" 
                  description="Higher values may produce more false positives"
                >
                  <div className="w-48">
                    <Slider 
                      value={[settings.detectionSensitivity]} 
                      onValueChange={handleSliderChange('detectionSensitivity')}
                      min={10}
                      max={100}
                      step={5}
                    />
                    <div className="flex justify-between mt-1">
                      <span className="text-xs">Low</span>
                      <span className="text-xs">{settings.detectionSensitivity}%</span>
                      <span className="text-xs">High</span>
                    </div>
                  </div>
                </SettingItem>
              </div>
            </ConfigSection>
          </TabsContent>
          
          <TabsContent value="api">
            <ConfigSection
              title="API Integration"
              description="Connect to external services for enhanced functionality"
              icon={<Network className="w-4 h-4" />}
            >
              <div className="space-y-4">
                <div>
                  <Label htmlFor="rugCheckApiKey" className="mb-1 block">
                    RugCheck.xyz API Key
                  </Label>
                  <div className="flex gap-2">
                    <Input
                      id="rugCheckApiKey"
                      type="password"
                      value={settings.rugCheckApiKey}
                      onChange={handleInputChange('rugCheckApiKey')}
                      placeholder="Enter your RugCheck API key"
                      className="flex-1"
                    />
                    <Button variant="outline" size="icon">
                      <RefreshCw className="w-4 h-4" />
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Required for contract security verification
                  </p>
                </div>
                
                <div>
                  <Label htmlFor="pocketUniverseApiKey" className="mb-1 block">
                    Pocket Universe API Key
                  </Label>
                  <div className="flex gap-2">
                    <Input
                      id="pocketUniverseApiKey"
                      type="password"
                      value={settings.pocketUniverseApiKey}
                      onChange={handleInputChange('pocketUniverseApiKey')}
                      placeholder="Enter your Pocket Universe API key"
                      className="flex-1"
                    />
                    <Button variant="outline" size="icon">
                      <RefreshCw className="w-4 h-4" />
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Used for volume verification and fake liquidity detection
                  </p>
                </div>
                
                <div>
                  <Label htmlFor="dexScreenerApiKey" className="mb-1 block">
                    DexScreener API Key
                  </Label>
                  <div className="flex gap-2">
                    <Input
                      id="dexScreenerApiKey"
                      type="password"
                      value={settings.dexScreenerApiKey}
                      onChange={handleInputChange('dexScreenerApiKey')}
                      placeholder="Enter your DexScreener API key"
                      className="flex-1"
                    />
                    <Button variant="outline" size="icon">
                      <RefreshCw className="w-4 h-4" />
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Required for token discovery and price monitoring
                  </p>
                </div>
              </div>
              
              <div className="mt-6 p-3 bg-info/10 border border-info/20 rounded-md">
                <div className="flex gap-2">
                  <LineChart className="w-5 h-5 text-info flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">API Usage Statistics</p>
                    <p className="text-xs mt-1">
                      DexScreener: 1,458/2,000 calls (73%) <br />
                      RugCheck: 253/500 calls (51%) <br />
                      Pocket Universe: 78/100 calls (78%)
                    </p>
                  </div>
                </div>
              </div>
            </ConfigSection>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ConfigPanel;
