
import { useState } from 'react';
import Header from './Header';
import { cn } from '@/lib/utils';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const [isRunning, setIsRunning] = useState(true);
  
  const toggleRunning = () => {
    setIsRunning(prev => !prev);
  };
  
  return (
    <div className={cn(
      "min-h-screen bg-gradient-to-br from-background to-muted transition-colors duration-300",
    )}>
      <Header isRunning={isRunning} onToggleRunning={toggleRunning} />
      <main>
        {children}
      </main>
      <div className="fixed bottom-0 left-0 right-0 h-1.5 bg-gradient-subtle z-50" />
    </div>
  );
};

export default Layout;
