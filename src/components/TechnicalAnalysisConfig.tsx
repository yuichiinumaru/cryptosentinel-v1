
import { useState } from 'react';
import { Brain, TrendingUp, Activity, Zap, BarChart3, BarChart2, LineChart, GitBranch } from 'lucide-react';
import { Switch } from '@/components/ui/switch';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';

const TechnicalAnalysisConfig = () => {
  const [selectedIndicators, setSelectedIndicators] = useState<string[]>([
    'movingAverages',
    'rsi',
    'macd'
  ]);
  
  const handleToggleIndicator = (indicator: string) => {
    setSelectedIndicators(prev => 
      prev.includes(indicator) 
        ? prev.filter(i => i !== indicator) 
        : [...prev, indicator]
    );
  };
  
  const [timeframeValue, setTimeframeValue] = useState('1h');
  
  return (
    <div className="glass-panel rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-medium">Technical Analysis</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">Auto-adjust</span>
          <Switch 
            checked={true} 
            onCheckedChange={() => {}} 
          />
        </div>
      </div>
      
      <div className="p-4">
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium mb-3">Timeframe</h4>
            <ToggleGroup 
              type="single" 
              value={timeframeValue}
              onValueChange={(value) => value && setTimeframeValue(value)} 
              className="flex flex-wrap gap-1"
            >
              <ToggleGroupItem value="1m" className="text-xs">1m</ToggleGroupItem>
              <ToggleGroupItem value="5m" className="text-xs">5m</ToggleGroupItem>
              <ToggleGroupItem value="15m" className="text-xs">15m</ToggleGroupItem>
              <ToggleGroupItem value="1h" className="text-xs">1h</ToggleGroupItem>
              <ToggleGroupItem value="4h" className="text-xs">4h</ToggleGroupItem>
              <ToggleGroupItem value="1d" className="text-xs">1d</ToggleGroupItem>
            </ToggleGroup>
          </div>
          
          <div>
            <h4 className="text-sm font-medium mb-3">Indicators</h4>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="movingAverages" 
                  checked={selectedIndicators.includes('movingAverages')}
                  onCheckedChange={() => handleToggleIndicator('movingAverages')}
                />
                <Label htmlFor="movingAverages">Moving Averages</Label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="rsi" 
                  checked={selectedIndicators.includes('rsi')}
                  onCheckedChange={() => handleToggleIndicator('rsi')}
                />
                <Label htmlFor="rsi">RSI</Label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="macd" 
                  checked={selectedIndicators.includes('macd')}
                  onCheckedChange={() => handleToggleIndicator('macd')}
                />
                <Label htmlFor="macd">MACD</Label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="volume" 
                  checked={selectedIndicators.includes('volume')}
                  onCheckedChange={() => handleToggleIndicator('volume')}
                />
                <Label htmlFor="volume">Volume</Label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="supportResistance" 
                  checked={selectedIndicators.includes('supportResistance')}
                  onCheckedChange={() => handleToggleIndicator('supportResistance')}
                />
                <Label htmlFor="supportResistance">Support & Resistance</Label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TechnicalAnalysisConfig;
