import { useState, useEffect } from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  LineChart, Line
} from 'recharts';
import { cn } from '@/lib/utils';
import { api } from '@/services/api';

interface PriceChartProps {
  className?: string;
  height?: number;
  showVolume?: boolean;
  isCompact?: boolean;
  periodOptions?: string[];
  tokeName?: string;
}

const PriceChart = ({
  className,
  height = 300,
  showVolume = true,
  isCompact = false,
  periodOptions = ['1H', '1D', '1W', '1M', 'ALL'],
  tokeName = 'ETH/USDT'
}: PriceChartProps) => {
  const [data, setData] = useState<any[]>([]);
  const [activePeriod, setActivePeriod] = useState('1D');
  const [isLoading, setIsLoading] = useState(true);
  const [isBullish, setIsBullish] = useState(true);

  useEffect(() => {
    const fetchPriceData = async () => {
      setIsLoading(true);
      try {
        const symbol = tokeName.split('/')[0];
        const priceData = await api.market.getPriceData(symbol, activePeriod);
        
        if (priceData && priceData.length > 0) {
          setData(priceData);
          setIsBullish(priceData[0].price < priceData[priceData.length - 1].price);
        }
      } catch (error) {
        console.error('Failed to fetch price data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPriceData();
  }, [activePeriod, tokeName]);

  const formatTime = (time: string) => {
    const date = new Date(time);
    
    if (activePeriod === '1H') {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (activePeriod === '1D') {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  const formatPrice = (price: number) => {
    return `$${price.toFixed(2)}`;
  };

  return (
    <div className={cn("glass-panel rounded-lg p-4", className)}>
      {!isCompact && (
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="text-lg font-medium">{tokeName}</h3>
            {data.length > 0 && (
              <div className="flex items-center mt-1">
                <span className="text-2xl font-semibold mr-2">
                  {formatPrice(data[data.length - 1]?.price)}
                </span>
                <span 
                  className={cn(
                    "text-sm font-medium",
                    isBullish ? "text-success" : "text-destructive"
                  )}
                >
                  {isBullish ? '↑' : '↓'} 
                  {isBullish 
                    ? ((data[data.length - 1]?.price / data[0]?.price - 1) * 100).toFixed(2) 
                    : ((1 - data[data.length - 1]?.price / data[0]?.price) * 100).toFixed(2)
                  }%
                </span>
              </div>
            )}
          </div>
          
          <div className="flex space-x-1">
            {periodOptions.map(period => (
              <button
                key={period}
                onClick={() => setActivePeriod(period)}
                className={cn(
                  "px-2 py-1 text-xs font-medium rounded transition-colors",
                  activePeriod === period 
                    ? "bg-primary text-primary-foreground" 
                    : "text-muted-foreground hover:bg-secondary"
                )}
              >
                {period}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {isLoading ? (
        <div className="flex justify-center items-center h-[200px]">
          <div className="animate-pulse bg-secondary rounded-md h-[180px] w-full" />
        </div>
      ) : (
        <div className={cn("transition-all duration-300", isLoading ? "opacity-0" : "opacity-100")}>
          <ResponsiveContainer width="100%" height={height}>
            <AreaChart data={data} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
              <defs>
                <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop 
                    offset="5%" 
                    stopColor={isBullish ? "#10B981" : "#EF4444"} 
                    stopOpacity={0.3} 
                  />
                  <stop 
                    offset="95%" 
                    stopColor={isBullish ? "#10B981" : "#EF4444"} 
                    stopOpacity={0} 
                  />
                </linearGradient>
              </defs>
              
              {!isCompact && (
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  vertical={false} 
                  stroke="rgba(255,255,255,0.1)" 
                />
              )}
              
              <XAxis 
                dataKey="time" 
                tickFormatter={formatTime} 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: 'var(--muted-foreground)' }}
                minTickGap={30}
                hide={isCompact}
              />
              
              <YAxis 
                domain={['dataMin', 'dataMax']} 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: 'var(--muted-foreground)' }}
                orientation="right"
                hide={isCompact}
              />
              
              {!isCompact && <Tooltip content={<CustomTooltip />} />}
              
              <Area 
                type="monotone" 
                dataKey="price" 
                stroke={isBullish ? "#10B981" : "#EF4444"} 
                fillOpacity={1}
                fill="url(#priceGradient)" 
              />
            </AreaChart>
          </ResponsiveContainer>
          
          {showVolume && !isCompact && (
            <div className="mt-2 h-16">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data}>
                  <defs>
                    <linearGradient id="volumeGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366F1" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#6366F1" stopOpacity={0.3} />
                    </linearGradient>
                  </defs>
                  <Bar dataKey="volume" fill="url(#volumeGradient)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-panel rounded p-2 shadow-lg">
        <p className="text-sm font-medium">
          {new Date(label).toLocaleString([], {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })}
        </p>
        <p className="text-sm font-semibold">
          Price: ${payload[0].value.toFixed(2)}
        </p>
        {payload[1] && (
          <p className="text-xs">
            Volume: {payload[1].value.toLocaleString()}
          </p>
        )}
      </div>
    );
  }
  return null;
};

const BarChart = ({ data, children }: any) => (
  <LineChart data={data} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
    {children}
  </LineChart>
);

const Bar = ({ dataKey, fill }: any) => (
  <Line 
    type="monotone" 
    dataKey={dataKey} 
    stroke="#6366F1" 
    strokeWidth={1}
    dot={false}
  />
);

export default PriceChart;
