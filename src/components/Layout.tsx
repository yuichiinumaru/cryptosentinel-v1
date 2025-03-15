
import { useState, useEffect } from 'react';
import Header from './Header';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Moon, Sun, Terminal, Shield } from 'lucide-react';
import NewsTickerBar from './NewsTickerBar';

interface LayoutProps {
  children: React.ReactNode;
}

type Theme = 'light' | 'tactical-dark' | 'dark-grey' | 'mr-robot';

const Layout = ({ children }: LayoutProps) => {
  const [isRunning, setIsRunning] = useState(true);
  const [theme, setTheme] = useState<Theme>('light');
  
  const toggleRunning = () => {
    setIsRunning(prev => !prev);
  };
  
  useEffect(() => {
    // Check if theme is stored in localStorage
    const savedTheme = localStorage.getItem('theme') as Theme | null;
    if (savedTheme) {
      setTheme(savedTheme);
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setTheme('tactical-dark');
    }
  }, []);
  
  useEffect(() => {
    // Update HTML element classes based on the selected theme
    const htmlElement = document.documentElement;
    
    // Remove all theme classes
    htmlElement.classList.remove('dark', 'theme-dark-grey', 'theme-mr-robot', 'theme-tactical-dark');
    
    // Add the appropriate theme class
    if (theme === 'tactical-dark') {
      htmlElement.classList.add('theme-tactical-dark');
    } else if (theme === 'dark-grey') {
      htmlElement.classList.add('theme-dark-grey');
    } else if (theme === 'mr-robot') {
      htmlElement.classList.add('theme-mr-robot');
    }
    
    // Save theme preference to localStorage
    localStorage.setItem('theme', theme);
  }, [theme]);
  
  // Mr. Robot theme specific elements
  const renderMrRobotElements = () => {
    if (theme === 'mr-robot') {
      return (
        <>
          <div className="scanline"></div>
          <div className="matrix-bg"></div>
        </>
      );
    }
    return null;
  };
  
  return (
    <div className={cn(
      "min-h-screen flex flex-col transition-colors duration-300",
      theme === 'mr-robot' && "bg-black crt-flicker"
    )}>
      <Header isRunning={isRunning} onToggleRunning={toggleRunning} />
      
      <div className="fixed right-4 top-20 z-50 flex flex-col gap-2">
        <Button
          variant="outline"
          size="icon"
          onClick={() => setTheme('light')}
          className={cn(
            "rounded-full",
            theme === 'light' ? "bg-primary text-primary-foreground" : "bg-background/50 backdrop-blur-sm"
          )}
        >
          <Sun className="h-[1.2rem] w-[1.2rem]" />
          <span className="sr-only">Light mode</span>
        </Button>
        
        <Button
          variant="outline"
          size="icon"
          onClick={() => setTheme('tactical-dark')}
          className={cn(
            "rounded-full",
            theme === 'tactical-dark' ? "bg-primary text-primary-foreground" : "bg-background/50 backdrop-blur-sm"
          )}
        >
          <Shield className="h-[1.2rem] w-[1.2rem]" />
          <span className="sr-only">Tactical Dark mode</span>
        </Button>
        
        <Button
          variant="outline"
          size="icon"
          onClick={() => setTheme('dark-grey')}
          className={cn(
            "rounded-full",
            theme === 'dark-grey' ? "bg-primary text-primary-foreground" : "bg-background/50 backdrop-blur-sm"
          )}
        >
          <Moon className="h-[1.2rem] w-[1.2rem]" />
          <span className="sr-only">Dark Grey theme</span>
        </Button>
        
        <Button
          variant="outline"
          size="icon"
          onClick={() => setTheme('mr-robot')}
          className={cn(
            "rounded-full",
            theme === 'mr-robot' ? "bg-primary text-primary-foreground" : "bg-background/50 backdrop-blur-sm"
          )}
        >
          <Terminal className="h-[1.2rem] w-[1.2rem]" />
          <span className="sr-only">Mr. Robot theme</span>
        </Button>
      </div>
      
      <main className="flex-1 overflow-auto">
        {children}
      </main>
      
      {/* News ticker at the bottom */}
      <NewsTickerBar />
      
      <div className="fixed bottom-0 left-0 right-0 h-1.5 bg-gradient-subtle z-40" />
      
      {renderMrRobotElements()}
    </div>
  );
};

export default Layout;
