
import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { 
  Play, Pause, Settings, Menu, 
  X, Wallet, ChevronDown, LineChart,
  Home, Bell, BookText, Shield
} from 'lucide-react';
import StatusIndicator from './StatusIndicator';
import { cn } from '@/lib/utils';

interface HeaderProps {
  isRunning: boolean;
  onToggleRunning: () => void;
}

const Header = ({ isRunning, onToggleRunning }: HeaderProps) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  
  const toggleMenu = () => {
    setIsMenuOpen(prev => !prev);
  };
  
  const navItems = [
    { name: "Dashboard", href: "/", icon: Home },
    { name: "Analytics", href: "/analytics", icon: LineChart },
    { name: "Wallet", href: "/wallet", icon: Wallet },
    { name: "News", href: "/news", icon: BookText },
    { name: "Notifications", href: "/notifications", icon: Bell },
    { name: "Security", href: "/security", icon: Shield },
    { name: "Settings", href: "/settings", icon: Settings },
  ];
  
  return (
    <header className="glass-panel sticky top-0 z-50 backdrop-blur-xl border-b border-border">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="hidden sm:flex items-center">
            <Logo />
          </div>
          
          <div className="flex sm:hidden">
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={toggleMenu}
              className="text-foreground"
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>
        
        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-1">
          {navItems.map((item) => (
            <Button
              key={item.href}
              variant="ghost"
              size="sm"
              asChild
              className={cn(
                "gap-1.5",
                (location.pathname === item.href || location.pathname === item.href.toLowerCase()) && 
                "bg-muted text-foreground"
              )}
            >
              <Link to={item.href}>
                <item.icon className="w-4 h-4 mr-1" />
                {item.name}
              </Link>
            </Button>
          ))}
        </div>
        
        <div className="flex items-center gap-3">
          <StatusBadge isRunning={isRunning} />
          
          <div className="hidden sm:flex items-center gap-3">
            <Button 
              variant={isRunning ? "outline" : "default"}
              size="sm"
              onClick={onToggleRunning}
              className="gap-1.5"
            >
              {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              {isRunning ? "Pause Bot" : "Start Bot"}
            </Button>
            
            <WalletButton />
          </div>
        </div>
      </div>
      
      {/* Mobile menu */}
      <div className={cn(
        "sm:hidden absolute w-full bg-background border-b border-border transition-all duration-300 overflow-hidden",
        isMenuOpen ? "max-h-screen opacity-100" : "max-h-0 opacity-0"
      )}>
        <div className="container mx-auto p-4 space-y-4">
          <div className="flex justify-between items-center">
            <Logo />
            <Button 
              variant={isRunning ? "outline" : "default"}
              onClick={onToggleRunning}
              className="gap-1.5"
            >
              {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              {isRunning ? "Pause Bot" : "Start Bot"}
            </Button>
          </div>
          
          <div className="flex flex-col gap-2">
            {navItems.map((item) => (
              <Button 
                key={item.href}
                variant="outline" 
                asChild
                className={cn(
                  "gap-1.5 justify-start w-full",
                  (location.pathname === item.href || location.pathname === item.href.toLowerCase()) && 
                  "bg-muted border-primary"
                )}
              >
                <Link to={item.href}>
                  <item.icon className="w-4 h-4 mr-2" />
                  {item.name}
                </Link>
              </Button>
            ))}
            <div className="flex justify-between items-center mt-2">
              <WalletButton fullWidth />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

const Logo = () => (
  <div className="flex items-center gap-2">
    <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
      <div className="text-primary-foreground font-bold">CS</div>
    </div>
    <div className="font-medium text-lg">CryptoSentinel</div>
  </div>
);

const StatusBadge = ({ isRunning }: { isRunning: boolean }) => (
  <div className="glass-panel rounded-full py-1 px-3 flex items-center gap-2">
    <StatusIndicator status={isRunning ? "online" : "offline"} />
    <span className="text-xs font-medium">
      {isRunning ? "Active" : "Paused"}
    </span>
  </div>
);

const WalletButton = ({ fullWidth = false }: { fullWidth?: boolean }) => (
  <Button 
    variant="outline" 
    className={cn(
      "gap-1.5 bg-secondary/50",
      fullWidth && "w-full justify-between"
    )}
  >
    <Wallet className="w-4 h-4" />
    <span>0x7a...3e9f</span>
    <ChevronDown className="w-4 h-4" />
  </Button>
);

export default Header;
