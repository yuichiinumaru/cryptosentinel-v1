
import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';

type Status = 'online' | 'offline' | 'error' | 'warning';

interface StatusIndicatorProps {
  status: Status;
  pulseEffect?: boolean;
  label?: string;
  className?: string;
}

const StatusIndicator = ({ 
  status, 
  pulseEffect = true, 
  label,
  className 
}: StatusIndicatorProps) => {
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    // Trigger animation on status change
    setIsAnimating(true);
    const timer = setTimeout(() => setIsAnimating(false), 1000);
    return () => clearTimeout(timer);
  }, [status]);

  const getStatusColor = () => {
    switch (status) {
      case 'online':
        return 'bg-success';
      case 'offline':
        return 'bg-muted-foreground';
      case 'error':
        return 'bg-destructive';
      case 'warning':
        return 'bg-warning';
      default:
        return 'bg-muted-foreground';
    }
  };

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <span 
        className={cn(
          "relative inline-flex h-3 w-3 rounded-full transition-all duration-300 transform",
          getStatusColor(),
          isAnimating && "scale-125",
          pulseEffect && "after:content-[''] after:absolute after:h-3 after:w-3 after:rounded-full after:opacity-75 after:animate-pulse-subtle",
          pulseEffect && getStatusColor().replace('bg-', 'after:bg-')
        )}
      />
      {label && (
        <span className="text-xs font-medium text-muted-foreground">
          {label}
        </span>
      )}
    </div>
  );
};

export default StatusIndicator;
