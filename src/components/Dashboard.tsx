
import { useState, useEffect } from 'react';
import { Activity, TrendingUp, ShieldAlert, Brain, Zap } from 'lucide-react';
import { useFadeIn } from '@/utils/animations';
import MetricsCard from './MetricsCard';
import PriceChart from './PriceChart';
import TradeList from './TradeList';
import BlacklistManager from './BlacklistManager';
import ConfigPanel from './ConfigPanel';
import AILearningSystem from './AILearningSystem';
import TechnicalAnalysisConfig from './TechnicalAnalysisConfig';
import AgentActivityMonitor from './AgentActivityMonitor';

const generateRandomData = (points: number) => {
  return Array.from({ length: points }).map(() => ({
    value: Math.floor(Math.random() * 100)
  }));
};

const Dashboard = () => {
  const [isLoading, setIsLoading] = useState(true);
  const fadeInStyle = useFadeIn(300);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);
  
  return (
    <div className="container mx-auto p-4 lg:p-6 space-y-6 pb-20" style={fadeInStyle}>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricsCard
          title="Daily Profit"
          value="+$128.45"
          change={12.5}
          data={generateRandomData(20)}
          icon={<TrendingUp className="w-5 h-5" />}
          variant="success"
        />
        
        <MetricsCard
          title="Trades Today"
          value="24"
          change={-8.2}
          data={generateRandomData(20)}
          icon={<Activity className="w-5 h-5" />}
          variant="info"
        />
        
        <MetricsCard
          title="Scams Avoided"
          value="17"
          change={42}
          data={generateRandomData(20)}
          icon={<ShieldAlert className="w-5 h-5" />}
          variant="warning"
        />
        
        <MetricsCard
          title="AI Confidence"
          value="86%"
          change={3.4}
          data={generateRandomData(20)}
          icon={<Brain className="w-5 h-5" />}
          variant="default"
        />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium">Hot Opportunities</h2>
              <div className="badge badge-success">
                <Zap className="w-3 h-3 mr-1" />
                Live Tracking
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <OpportunityCard 
                name="PEPE"
                address="0x6982508145454ce325ddbe47a25d4ec3d2311933"
                change={+18.5}
                liquidity="$5.2M"
                confidence={92}
              />
              
              <OpportunityCard 
                name="SHIB"
                address="0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce"
                change={+7.2}
                liquidity="$28.9M"
                confidence={88}
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 gap-6">
            <AgentActivityMonitor />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <PriceChart height={300} />
            <TradeList />
          </div>
          
          <div className="grid grid-cols-1 gap-6">
            <AILearningSystem />
          </div>
          
          <BlacklistManager />
        </div>
        
        <div className="lg:col-span-1 space-y-6">
          <ConfigPanel />
          <TechnicalAnalysisConfig />
        </div>
      </div>
    </div>
  );
};

interface OpportunityCardProps {
  name: string;
  address: string;
  change: number;
  liquidity: string;
  confidence: number;
}

const OpportunityCard = ({ name, address, change, liquidity, confidence }: OpportunityCardProps) => (
  <div className="bg-secondary/30 rounded-lg p-4 hover:bg-secondary/50 transition-colors">
    <div className="flex justify-between items-start">
      <div>
        <div className="text-lg font-medium">{name}</div>
        <div className="text-xs text-muted-foreground font-mono">
          {address.substring(0, 6)}...{address.substring(address.length - 4)}
        </div>
        
        <div className="mt-3 space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">24h Change</span>
            <span className="text-sm font-medium text-success">+{change}%</span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Liquidity</span>
            <span className="text-sm">{liquidity}</span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">AI Confidence</span>
            <span className="text-sm">{confidence}%</span>
          </div>
        </div>
      </div>
      
      <div className="h-16 w-24 mt-1">
        <PriceChart 
          height={60}
          showVolume={false}
          isCompact={true}
        />
      </div>
    </div>
    
    <div className="mt-4 flex space-x-2">
      <button className="bg-primary text-primary-foreground px-3 py-1.5 rounded text-sm font-medium flex-1 hover:bg-primary/90 transition-colors">
        Buy
      </button>
      <button className="bg-muted text-muted-foreground px-3 py-1.5 rounded text-sm flex-1 hover:bg-muted/80 transition-colors">
        Analyze
      </button>
    </div>
  </div>
);

export default Dashboard;
