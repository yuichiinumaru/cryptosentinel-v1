
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Newspaper, Zap, ArrowUpRight, ArrowDownRight, Filter, RefreshCw, ExternalLink } from 'lucide-react';
import { NewsItem, agency } from '@/lib/agencySwarm';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

const NewsFeed = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [activeTab, setActiveTab] = useState('all');
  const [activeFilter, setActiveFilter] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // Initial load of news
    setNews(agency.getNews());
    setIsLoading(false);
    
    // Subscribe to news updates
    const handleNewsUpdate = (newsItem: NewsItem) => {
      setNews(prevNews => [newsItem, ...prevNews].slice(0, 100));
    };
    
    agency.on('news', handleNewsUpdate);
    
    return () => {
      agency.off('news', handleNewsUpdate);
    };
  }, []);
  
  // Filter news based on active tab and filters
  const filteredNews = news.filter(item => {
    // Filter by sentiment tab
    if (activeTab === 'positive' && item.sentiment !== 'positive') return false;
    if (activeTab === 'negative' && item.sentiment !== 'negative') return false;
    if (activeTab === 'neutral' && item.sentiment !== 'neutral') return false;
    
    // Filter by tags if activeFilter is not empty
    if (activeFilter.length > 0) {
      return item.tags.some(tag => activeFilter.includes(tag)) || 
             (item.coins && item.coins.some(coin => activeFilter.includes(coin)));
    }
    
    return true;
  });
  
  // Get all unique tags for filtering
  const allTags = [...new Set(news.flatMap(item => [...item.tags, ...(item.coins || [])]))]
    .sort()
    .filter(Boolean);
  
  const refreshNews = () => {
    setIsLoading(true);
    setTimeout(() => {
      setNews(agency.getNews());
      setIsLoading(false);
    }, 1000);
  };
  
  const toggleFilter = (filter: string) => {
    setActiveFilter(prev => 
      prev.includes(filter) 
        ? prev.filter(f => f !== filter)
        : [...prev, filter]
    );
  };
  
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'bg-green-500/10 text-green-500 hover:bg-green-500/20';
      case 'negative': return 'bg-red-500/10 text-red-500 hover:bg-red-500/20';
      case 'neutral': return 'bg-blue-500/10 text-blue-500 hover:bg-blue-500/20';
      default: return 'bg-gray-500/10 text-gray-500';
    }
  };
  
  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return <ArrowUpRight className="h-3 w-3 mr-1" />;
      case 'negative': return <ArrowDownRight className="h-3 w-3 mr-1" />;
      default: return null;
    }
  };
  
  return (
    <div className="glass-panel rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Newspaper className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-medium">News Feed</h3>
          <Badge variant="outline" className="ml-2 bg-primary/10">
            <Zap className="mr-1 h-3 w-3" />
            AI Powered
          </Badge>
        </div>
        <Button size="sm" variant="outline" onClick={refreshNews} disabled={isLoading}>
          <RefreshCw className={cn("h-4 w-4 mr-1", isLoading && "animate-spin")} />
          Refresh
        </Button>
      </div>
      
      <div className="p-4">
        <div className="flex flex-wrap gap-2 mb-4">
          <Filter className="w-4 h-4 mr-1 opacity-70" />
          {allTags.slice(0, 8).map(tag => (
            <Badge 
              key={tag}
              variant={activeFilter.includes(tag) ? "default" : "outline"}
              className="cursor-pointer"
              onClick={() => toggleFilter(tag)}
            >
              {tag}
            </Badge>
          ))}
          {allTags.length > 8 && (
            <Badge variant="outline" className="cursor-pointer">
              +{allTags.length - 8} more
            </Badge>
          )}
        </div>
        
        <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-4 mb-4">
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="positive">Bullish</TabsTrigger>
            <TabsTrigger value="negative">Bearish</TabsTrigger>
            <TabsTrigger value="neutral">Neutral</TabsTrigger>
          </TabsList>
          
          <TabsContent value={activeTab} className="mt-0">
            <ScrollArea className="h-[400px] pr-4">
              <div className="space-y-3">
                {isLoading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <Card key={i} className="animate-pulse">
                      <CardHeader className="pb-2">
                        <div className="h-5 w-3/4 bg-muted rounded"></div>
                        <div className="h-4 w-1/2 bg-muted rounded mt-2"></div>
                      </CardHeader>
                      <CardContent>
                        <div className="h-4 w-full bg-muted rounded"></div>
                        <div className="h-4 w-full bg-muted rounded mt-2"></div>
                      </CardContent>
                    </Card>
                  ))
                ) : filteredNews.length > 0 ? (
                  filteredNews.map(newsItem => (
                    <Card key={newsItem.id}>
                      <CardHeader className="pb-2">
                        <div className="flex justify-between items-start">
                          <CardTitle className="text-base">{newsItem.title}</CardTitle>
                          <Badge 
                            variant="outline" 
                            className={cn("border-0", getSentimentColor(newsItem.sentiment))}
                          >
                            {getSentimentIcon(newsItem.sentiment)}
                            {newsItem.sentiment.charAt(0).toUpperCase() + newsItem.sentiment.slice(1)}
                          </Badge>
                        </div>
                        <CardDescription className="flex items-center text-xs">
                          {newsItem.source} • {new Date(newsItem.timestamp).toLocaleString()}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm">{newsItem.summary}</p>
                        
                        <div className="flex flex-wrap gap-1 mt-2">
                          {newsItem.tags.map(tag => (
                            <Badge 
                              key={tag} 
                              variant="outline" 
                              className="text-xs bg-secondary/50"
                            >
                              {tag}
                            </Badge>
                          ))}
                          {newsItem.coins && newsItem.coins.map(coin => (
                            <Badge 
                              key={coin} 
                              variant="outline" 
                              className="text-xs bg-primary/10"
                            >
                              {coin}
                            </Badge>
                          ))}
                        </div>
                      </CardContent>
                      {newsItem.url && (
                        <CardFooter className="pt-0">
                          <Button variant="link" size="sm" className="p-0 h-auto" asChild>
                            <a href={newsItem.url} target="_blank" rel="noopener noreferrer">
                              Read full article <ExternalLink className="ml-1 h-3 w-3" />
                            </a>
                          </Button>
                        </CardFooter>
                      )}
                      <div className="px-6 pb-3">
                        <div className="text-xs text-muted-foreground">
                          Analyzed by: {agency.getAgent(newsItem.agentId)?.name || "AI Agent"}
                        </div>
                      </div>
                    </Card>
                  ))
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    No news matching your filters
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
        
        <Separator className="my-4" />
        
        <div className="text-xs text-muted-foreground">
          News is analyzed by a team of AI agents in real-time. The MarketAnalyst agent continuously scans multiple sources for relevant news and analyzes their sentiment and potential market impact.
        </div>
      </div>
    </div>
  );
};

export default NewsFeed;
