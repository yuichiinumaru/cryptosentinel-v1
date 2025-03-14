
import { useState, useEffect, useRef } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowUpRight, ArrowDownRight, Newspaper, Zap, ChevronUp, ChevronDown } from 'lucide-react';
import { NewsItem, agency } from '@/lib/agencySwarm';
import { cn } from '@/lib/utils';

const NewsTickerBar = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initial load of news
    setNews(agency.getNews());
    
    // Subscribe to news updates
    const handleNewsUpdate = (newsItem: NewsItem) => {
      setNews(prevNews => [newsItem, ...prevNews].slice(0, 20));
    };
    
    agency.on('news', handleNewsUpdate);
    
    return () => {
      agency.off('news', handleNewsUpdate);
    };
  }, []);

  // Auto-scroll the ticker
  useEffect(() => {
    if (!scrollRef.current || isExpanded) return;
    
    const scrollContainer = scrollRef.current;
    let animationId: number;
    let position = 0;
    
    const scroll = () => {
      if (!scrollContainer) return;
      
      position += 0.5;
      if (position >= scrollContainer.scrollWidth / 2) {
        position = 0;
      }
      
      scrollContainer.scrollLeft = position;
      animationId = requestAnimationFrame(scroll);
    };
    
    animationId = requestAnimationFrame(scroll);
    
    return () => {
      cancelAnimationFrame(animationId);
    };
  }, [news, isExpanded]);
  
  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return <ArrowUpRight className="h-3 w-3 text-green-500" />;
      case 'negative': return <ArrowDownRight className="h-3 w-3 text-red-500" />;
      default: return null;
    }
  };
  
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-500';
      case 'negative': return 'text-red-500';
      case 'neutral': return 'text-blue-500';
      default: return '';
    }
  };

  const toggleExpanded = () => {
    setIsExpanded(prev => !prev);
  };

  return (
    <div className={cn(
      "fixed bottom-0 left-0 right-0 bg-background/80 backdrop-blur-lg border-t z-50 transition-all duration-300",
      isExpanded ? "h-64" : "h-10"
    )}>
      <div className="flex items-center justify-between px-4 h-10">
        <div className="flex items-center space-x-2">
          <Newspaper className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium">Latest News</span>
          <Badge variant="outline" className="bg-primary/10">
            <Zap className="mr-1 h-3 w-3" />
            Live
          </Badge>
        </div>
        
        <Button 
          variant="ghost" 
          size="icon" 
          className="h-6 w-6" 
          onClick={toggleExpanded}
        >
          {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
        </Button>
      </div>
      
      {isExpanded ? (
        <div className="p-2 h-[calc(100%-2.5rem)] overflow-y-auto">
          <div className="space-y-2">
            {news.length > 0 ? news.map((item) => (
              <div key={item.id} className="p-2 rounded-md bg-card text-sm">
                <div className="flex justify-between items-center">
                  <div className="font-medium">{item.title}</div>
                  <div className={cn("flex items-center", getSentimentColor(item.sentiment))}>
                    {getSentimentIcon(item.sentiment)}
                    <span className="text-xs ml-1">
                      {item.sentiment.charAt(0).toUpperCase() + item.sentiment.slice(1)}
                    </span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-1">{item.summary}</p>
                <div className="flex mt-1 gap-1 flex-wrap">
                  {item.coins && item.coins.map(coin => (
                    <Badge key={coin} variant="outline" className="text-xs bg-primary/10">
                      {coin}
                    </Badge>
                  ))}
                </div>
              </div>
            )) : (
              <div className="text-center py-4 text-muted-foreground">
                No news available
              </div>
            )}
          </div>
        </div>
      ) : (
        <div 
          ref={scrollRef}
          className="overflow-x-hidden whitespace-nowrap px-4"
        >
          {news.length > 0 ? (
            <div className="inline-block min-w-max">
              {news.map((item) => (
                <span key={item.id} className="inline-flex items-center mr-8">
                  {getSentimentIcon(item.sentiment)}
                  <span className={cn("ml-1 text-sm", getSentimentColor(item.sentiment))}>
                    {item.title}
                  </span>
                </span>
              ))}
              {/* Duplicate the news for continuous scrolling effect */}
              {news.map((item) => (
                <span key={`${item.id}-duplicate`} className="inline-flex items-center mr-8">
                  {getSentimentIcon(item.sentiment)}
                  <span className={cn("ml-1 text-sm", getSentimentColor(item.sentiment))}>
                    {item.title}
                  </span>
                </span>
              ))}
            </div>
          ) : (
            <div className="text-center text-muted-foreground">
              No news available
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NewsTickerBar;
