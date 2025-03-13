
import { useState } from 'react';
import { 
  Checkbox,
  Label 
} from '@/components/ui/checkbox';
import { Separator } from '@/components/ui/separator';
import { 
  Activity, TrendingUp, ChartBar, ChartLine, 
  LineChart, BarChart, AreaChart, BarChart2,
  Ruler, RotateCcw, Waves
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';

interface TechnicalIndicator {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  enabled: boolean;
}

const TechnicalAnalysisConfig = () => {
  const [indicators, setIndicators] = useState<TechnicalIndicator[]>([
    {
      id: 'moving-averages',
      name: 'Moving Averages',
      description: 'Identify trend direction and potential reversals',
      icon: <LineChart className="w-4 h-4" />,
      enabled: true
    },
    {
      id: 'rsi',
      name: 'Relative Strength Index',
      description: 'Measure speed and change of price movements',
      icon: <ChartLine className="w-4 h-4" />,
      enabled: true
    },
    {
      id: 'macd',
      name: 'Moving Average Convergence Divergence',
      description: 'Identify momentum and trend direction',
      icon: <Activity className="w-4 h-4" />,
      enabled: true
    },
    {
      id: 'bollinger',
      name: 'Bollinger Bands',
      description: 'Measure volatility and potential price targets',
      icon: <Waves className="w-4 h-4" />,
      enabled: false
    },
    {
      id: 'support-resistance',
      name: 'Support and Resistance',
      description: 'Identify key price levels where a trend may reverse',
      icon: <Ruler className="w-4 h-4" />,
      enabled: true
    },
    {
      id: 'trendlines',
      name: 'Trendlines',
      description: 'Visual representation of price direction',
      icon: <TrendingUp className="w-4 h-4" />,
      enabled: true
    },
    {
      id: 'chart-patterns',
      name: 'Chart Patterns',
      description: 'Recognize recurring patterns that signal reversals or continuations',
      icon: <AreaChart className="w-4 h-4" />,
      enabled: false
    },
    {
      id: 'fibonacci',
      name: 'Fibonacci Retracement',
      description: 'Identify potential support and resistance levels',
      icon: <RotateCcw className="w-4 h-4" />,
      enabled: false
    },
    {
      id: 'volume',
      name: 'Volume Analysis',
      description: 'Confirm price movements and trend strength',
      icon: <BarChart className="w-4 h-4" />,
      enabled: true
    },
    {
      id: 'stochastic',
      name: 'Stochastic Oscillator',
      description: 'Identify overbought and oversold conditions',
      icon: <ChartBar className="w-4 h-4" />,
      enabled: false
    }
  ]);
  
  const [strategyMode, setStrategyMode] = useState('autonomous');
  const [riskProfile, setRiskProfile] = useState(['medium']);

  const toggleIndicator = (id: string) => {
    setIndicators(indicators.map(indicator => 
      indicator.id === id 
        ? { ...indicator, enabled: !indicator.enabled } 
        : indicator
    ));
  };
  
  return (
    <div className="glass-panel rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-border flex items-center">
        <BarChart2 className="w-5 h-5 text-primary mr-2" />
        <h3 className="text-lg font-medium">Technical Analysis Configuration</h3>
      </div>
      
      <div className="p-6">
        <div className="mb-6">
          <h4 className="text-sm font-semibold mb-1">Strategy Mode</h4>
          <p className="text-xs text-muted-foreground mb-3">
            Select how the AI agent should apply technical analysis
          </p>
          
          <RadioGroup 
            value={strategyMode} 
            onValueChange={setStrategyMode}
            className="grid grid-cols-1 md:grid-cols-3 gap-2"
          >
            <Label 
              htmlFor="autonomous" 
              className={cn(
                "flex items-center border rounded-md px-4 py-3 gap-3 cursor-pointer transition-colors",
                strategyMode === 'autonomous' ? "bg-primary/10 border-primary" : "bg-background"
              )}
            >
              <RadioGroupItem value="autonomous" id="autonomous" />
              <div>
                <div className="font-medium">Autonomous</div>
                <div className="text-xs text-muted-foreground">AI decides when to use each indicator</div>
              </div>
            </Label>
            
            <Label 
              htmlFor="guided" 
              className={cn(
                "flex items-center border rounded-md px-4 py-3 gap-3 cursor-pointer transition-colors",
                strategyMode === 'guided' ? "bg-primary/10 border-primary" : "bg-background"
              )}
            >
              <RadioGroupItem value="guided" id="guided" />
              <div>
                <div className="font-medium">Guided</div>
                <div className="text-xs text-muted-foreground">Suggest but ask for confirmation</div>
              </div>
            </Label>
            
            <Label 
              htmlFor="passive" 
              className={cn(
                "flex items-center border rounded-md px-4 py-3 gap-3 cursor-pointer transition-colors",
                strategyMode === 'passive' ? "bg-primary/10 border-primary" : "bg-background"
              )}
            >
              <RadioGroupItem value="passive" id="passive" />
              <div>
                <div className="font-medium">Passive</div>
                <div className="text-xs text-muted-foreground">Only use indicators when requested</div>
              </div>
            </Label>
          </RadioGroup>
        </div>
        
        <div className="mb-6">
          <h4 className="text-sm font-semibold mb-1">Risk Profile</h4>
          <p className="text-xs text-muted-foreground mb-3">
            Define the trade aggressiveness based on technical signals
          </p>
          
          <ToggleGroup 
            type="single" 
            value={riskProfile} 
            onValueChange={(value) => {
              if (value) setRiskProfile([value]);
            }}
            className="justify-start"
          >
            <ToggleGroupItem value="conservative" size="sm">
              Conservative
            </ToggleGroupItem>
            <ToggleGroupItem value="medium" size="sm">
              Medium
            </ToggleGroupItem>
            <ToggleGroupItem value="aggressive" size="sm">
              Aggressive
            </ToggleGroupItem>
          </ToggleGroup>
        </div>
        
        <Separator className="my-6" />
        
        <div>
          <h4 className="text-sm font-semibold mb-1">Technical Indicators</h4>
          <p className="text-xs text-muted-foreground mb-4">
            Select which technical analysis methods the AI agent can use
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-3">
            {indicators.map(indicator => (
              <div 
                key={indicator.id}
                className="flex items-start space-x-3 py-2"
              >
                <Checkbox 
                  id={indicator.id} 
                  checked={indicator.enabled}
                  onCheckedChange={() => toggleIndicator(indicator.id)}
                  className="mt-0.5"
                />
                <div className="grid gap-1.5">
                  <div className="flex items-center">
                    {indicator.icon}
                    <Label 
                      htmlFor={indicator.id}
                      className="ml-2 font-medium text-sm"
                    >
                      {indicator.name}
                    </Label>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {indicator.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TechnicalAnalysisConfig;
