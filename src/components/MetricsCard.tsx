
import { useState, useEffect, ReactNode } from 'react';
import { AreaChart, Area, ResponsiveContainer, Tooltip } from 'recharts';
import { useFadeIn } from '@/utils/animations';
import { cn } from '@/lib/utils';

interface MetricsCardProps {
  title: string;
  value: string | number;
  change?: number;
  data?: Array<{ value: number }>;
  icon?: ReactNode;
  className?: string;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
}

const MetricsCard = ({
  title,
  value,
  change,
  data = [],
  icon,
  className,
  variant = 'default'
}: MetricsCardProps) => {
  const [isHovered, setIsHovered] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const fadeInStyle = useFadeIn(100);

  useEffect(() => {
    const timer = setTimeout(() => setHasLoaded(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const getVariantStyles = () => {
    switch (variant) {
      case 'success':
        return {
          chartColor: '#10B981',
          iconBackground: 'bg-success/10',
          iconColor: 'text-success'
        };
      case 'warning':
        return {
          chartColor: '#F59E0B',
          iconBackground: 'bg-warning/10',
          iconColor: 'text-warning dark:text-warning-foreground'
        };
      case 'danger':
        return {
          chartColor: '#EF4444',
          iconBackground: 'bg-destructive/10',
          iconColor: 'text-destructive'
        };
      case 'info':
        return {
          chartColor: '#0EA5E9',
          iconBackground: 'bg-info/10',
          iconColor: 'text-info dark:text-info-foreground'
        };
      default:
        return {
          chartColor: 'hsl(var(--primary))',
          iconBackground: 'bg-primary/10',
          iconColor: 'text-primary'
        };
    }
  };

  const variantStyles = getVariantStyles();

  return (
    <div 
      className={cn(
        "glass-panel rounded-lg px-5 py-4 glass-panel-hover", 
        className
      )}
      style={fadeInStyle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex justify-between items-start mb-3">
        <div className="flex flex-col">
          <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
          <p className="text-2xl font-semibold mt-1">{value}</p>
          
          {typeof change !== 'undefined' && (
            <div className="flex items-center mt-1">
              <span 
                className={cn(
                  "text-xs font-medium",
                  change >= 0 ? "text-success" : "text-destructive"
                )}
              >
                {change >= 0 ? '↑' : '↓'} {Math.abs(change)}%
              </span>
            </div>
          )}
        </div>
        
        {icon && (
          <div className={cn(
            "w-10 h-10 flex items-center justify-center rounded-full",
            variantStyles.iconBackground,
            variantStyles.iconColor
          )}>
            {icon}
          </div>
        )}
      </div>
      
      {data.length > 0 && (
        <div className={cn(
          "h-16 w-full transition-opacity duration-500",
          hasLoaded ? "opacity-100" : "opacity-0"
        )}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id={`gradient-${title}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={variantStyles.chartColor} stopOpacity={0.3} />
                  <stop offset="100%" stopColor={variantStyles.chartColor} stopOpacity={0} />
                </linearGradient>
              </defs>
              {isHovered && <Tooltip content={CustomTooltip} />}
              <Area 
                type="monotone"
                dataKey="value"
                stroke={variantStyles.chartColor}
                strokeWidth={1.5}
                fillOpacity={1}
                fill={`url(#gradient-${title})`}
                animationDuration={1000}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-panel rounded-lg py-1 px-2 text-xs shadow-lg">
        <p className="font-medium">{payload[0].value}</p>
      </div>
    );
  }
  return null;
};

export default MetricsCard;
