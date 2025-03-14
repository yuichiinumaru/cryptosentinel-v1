
import { useState, useEffect } from 'react';
import Header from './Header';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Moon, Sun, Terminal, Monitor } from 'lucide-react';
import {
  SidebarProvider,
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarTrigger,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  SidebarRail,
  SidebarInset,
} from '@/components/ui/sidebar';
import { Home, LineChart, Settings, Bell, BookText, Shield, Wallet } from 'lucide-react';
import { Link } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

type Theme = 'light' | 'dark' | 'dark-grey' | 'mr-robot';

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
      setTheme('dark');
    }
  }, []);
  
  useEffect(() => {
    // Update HTML element classes based on the selected theme
    const htmlElement = document.documentElement;
    
    // Remove all theme classes
    htmlElement.classList.remove('dark', 'theme-dark-grey', 'theme-mr-robot');
    
    // Add the appropriate theme class
    if (theme === 'dark') {
      htmlElement.classList.add('dark');
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
      return <div className="scanline"></div>;
    }
    return null;
  };

  const sidebarNavItems = [
    {
      name: "Dashboard",
      href: "/",
      icon: Home,
    },
    {
      name: "Analytics",
      href: "/analytics",
      icon: LineChart,
    },
    {
      name: "Wallet",
      href: "/wallet",
      icon: Wallet,
    },
    {
      name: "News Feed",
      href: "/news",
      icon: BookText,
    },
    {
      name: "Notifications",
      href: "/notifications",
      icon: Bell,
    },
    {
      name: "Security",
      href: "/security",
      icon: Shield,
    },
    {
      name: "Settings",
      href: "/settings",
      icon: Settings,
    },
  ];
  
  return (
    <SidebarProvider defaultOpen={true}>
      <div className={cn(
        "min-h-screen transition-colors duration-300",
        theme === 'mr-robot' && "bg-[#0a0f14] bg-noise"
      )}>
        <Sidebar variant="inset" collapsible="icon">
          <SidebarHeader>
            <div className="flex items-center gap-2 px-2">
              <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold">
                CS
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold truncate">CryptoSentinel</p>
                <p className="text-xs text-muted-foreground truncate">
                  Autonomous Trading Bot
                </p>
              </div>
              <SidebarTrigger />
            </div>
          </SidebarHeader>
          <SidebarContent>
            <SidebarMenu>
              {sidebarNavItems.map((item) => (
                <SidebarMenuItem key={item.href}>
                  <SidebarMenuButton
                    asChild
                    tooltip={item.name}
                    isActive={window.location.pathname === item.href}
                  >
                    <Link to={item.href}>
                      <item.icon className="mr-2" />
                      <span>{item.name}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarContent>
          <SidebarFooter>
            <div className="flex items-center justify-between p-2">
              <div className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
                <span className="text-xs">{isRunning ? 'Running' : 'Paused'}</span>
              </div>
            </div>
          </SidebarFooter>
          <SidebarRail />
        </Sidebar>
        
        <SidebarInset>
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
              onClick={() => setTheme('dark')}
              className={cn(
                "rounded-full",
                theme === 'dark' ? "bg-primary text-primary-foreground" : "bg-background/50 backdrop-blur-sm"
              )}
            >
              <Moon className="h-[1.2rem] w-[1.2rem]" />
              <span className="sr-only">Dark mode</span>
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
              <Monitor className="h-[1.2rem] w-[1.2rem]" />
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
          
          <main className="p-4 md:p-6 max-w-full">
            {children}
          </main>
          
          <div className="fixed bottom-0 left-0 right-0 h-1.5 bg-gradient-subtle z-50" />
          
          {renderMrRobotElements()}
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
};

export default Layout;
