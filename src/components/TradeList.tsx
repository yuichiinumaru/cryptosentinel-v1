import { useState, useEffect } from 'react';
import { useFadeIn, getStaggeredDelay } from '@/utils/animations';
import { cn } from '@/lib/utils';
import { api } from '@/services/api';

interface Trade {
  id: string;
  token: string;
  action: 'buy' | 'sell';
  amount: number;
  price: number;
  timestamp: Date;
  profit?: number;
  status: 'completed' | 'pending' | 'failed';
}

interface TradeListProps {
  className?: string;
  limit?: number;
}

const TradeList = ({ className, limit = 10 }: TradeListProps) => {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const fetchTrades = async () => {
      try {
        setIsLoading(true);
        const data = await api.trades.getRecent(limit);
        setTrades(data);
      } catch (error) {
        console.error('Failed to fetch trades:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchTrades();
  }, [limit]);
  
  const limitedTrades = trades.slice(0, limit);
  
  return (
    <div 
      className={cn(
        "glass-panel rounded-lg overflow-hidden",
        className
      )}
    >
      <div className="px-4 py-3 border-b border-border">
        <h3 className="text-lg font-medium">Recent Trades</h3>
      </div>
      
      <div className="max-h-[400px] overflow-y-auto subtle-scroll">
        {isLoading ? (
          <div className="p-4 space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="animate-pulse flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="h-10 w-10 rounded-full bg-secondary"></div>
                  <div className="space-y-2">
                    <div className="h-4 w-20 bg-secondary rounded"></div>
                    <div className="h-3 w-16 bg-secondary rounded"></div>
                  </div>
                </div>
                <div className="h-4 w-16 bg-secondary rounded"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="divide-y divide-border">
            {limitedTrades.length === 0 ? (
              <div className="p-6 text-center text-muted-foreground">
                No trades found
              </div>
            ) : (
              limitedTrades.map((trade, index) => (
                <TradeItem 
                  key={trade.id} 
                  trade={trade} 
                  delay={getStaggeredDelay(index)}
                />
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

const TradeItem = ({ trade, delay }: { trade: Trade, delay: number }) => {
  const fadeInStyle = useFadeIn(delay);
  
  const getStatusBadge = () => {
    switch (trade.status) {
      case 'completed':
        return (
          <span className="badge badge-success">
            Completed
          </span>
        );
      case 'pending':
        return (
          <span className="badge badge-warning">
            Pending
          </span>
        );
      case 'failed':
        return (
          <span className="badge badge-error">
            Failed
          </span>
        );
      default:
        return null;
    }
  };
  
  return (
    <div 
      className="px-4 py-3 hover:bg-secondary/30 transition-colors"
      style={fadeInStyle}
    >
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <div className={cn(
            "w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium",
            trade.action === 'buy' ? 'bg-success/10 text-success' : 'bg-destructive/10 text-destructive'
          )}>
            {trade.token}
          </div>
          
          <div>
            <div className="flex items-center">
              <span className={cn(
                "text-sm font-medium",
                trade.action === 'buy' ? 'text-success' : 'text-destructive'
              )}>
                {trade.action === 'buy' ? 'Bought' : 'Sold'}
              </span>
              <span className="mx-1.5 text-sm font-medium">
                {trade.amount} {trade.token}
              </span>
            </div>
            
            <div className="flex items-center mt-0.5 text-xs text-muted-foreground">
              <span>
                ${trade.price.toLocaleString()} • {' '}
                {new Date(trade.timestamp).toLocaleString(undefined, {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
            </div>
          </div>
        </div>
        
        <div className="text-right">
          {trade.profit !== undefined && (
            <div className={cn(
              "text-sm font-medium",
              trade.profit >= 0 ? 'text-success' : 'text-destructive'
            )}>
              {trade.profit >= 0 ? '+' : ''}{trade.profit}%
            </div>
          )}
          <div className="mt-0.5">
            {getStatusBadge()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradeList;
