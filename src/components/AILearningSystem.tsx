import { useState, useEffect } from 'react';
import { 
  Brain, Book, Database, RefreshCw, 
  ArrowUpRight, AlertCircle 
} from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Table, TableBody, TableCell, 
  TableHead, TableHeader, TableRow 
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { api } from '@/services/api';

const AILearningSystem = () => {
  const [learningData, setLearningData] = useState<any[]>([]);
  const [knowledgeData, setKnowledgeData] = useState<any>(null);
  const [isTraining, setIsTraining] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    fetchData();
  }, []);
  
  const fetchData = async () => {
    setIsLoading(true);
    try {
      const learnings = await api.learning.getLearnings();
      setLearningData(learnings);
      
      const knowledge = await api.learning.getDatabase();
      setKnowledgeData(knowledge);
    } catch (error) {
      console.error('Failed to fetch learning data:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const startTraining = async () => {
    setIsTraining(true);
    setTrainingProgress(0);
    
    try {
      await api.learning.trainModel();
      
      const interval = setInterval(() => {
        setTrainingProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            setIsTraining(false);
            fetchData();
            return 100;
          }
          return prev + 5;
        });
      }, 150);
    } catch (error) {
      console.error('Failed to start training:', error);
      setIsTraining(false);
    }
  };
  
  return (
    <div className="glass-panel rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-medium">AI Learning System</h3>
        </div>
        <Button 
          size="sm"
          variant="outline"
          onClick={startTraining}
          disabled={isTraining}
          className="gap-1.5"
        >
          <RefreshCw className={`w-4 h-4 ${isTraining ? 'animate-spin' : ''}`} /> 
          {isTraining ? 'Training...' : 'Retrain Model'}
        </Button>
      </div>
      
      {isTraining && (
        <div className="px-6 py-4 bg-muted/50">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium">Training AI Model</span>
            <span className="text-sm">{trainingProgress}%</span>
          </div>
          <Progress value={trainingProgress} className="h-2" />
          <div className="flex gap-4 mt-3 text-xs text-muted-foreground">
            <div>Processing trading history</div>
            <div>Analyzing patterns</div>
            <div>Updating weights</div>
          </div>
        </div>
      )}
      
      <div className="p-6">
        <Tabs defaultValue="learnings">
          <TabsList className="mb-4">
            <TabsTrigger value="learnings" className="flex items-center gap-1.5">
              <Book className="w-4 h-4" />
              <span>Learnings</span>
            </TabsTrigger>
            <TabsTrigger value="database" className="flex items-center gap-1.5">
              <Database className="w-4 h-4" />
              <span>Knowledge Database</span>
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="learnings">
            <div className="mb-4">
              <div className="bg-primary/10 p-3 rounded-md flex gap-3">
                <div className="p-2 bg-primary/20 rounded-full h-fit">
                  <Brain className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h4 className="text-sm font-medium">AI Learning Status</h4>
                  <p className="text-xs text-muted-foreground mt-1 mb-2">
                    The AI agent is continuously learning from trading outcomes and market observations to improve its strategy.
                  </p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    <Badge variant="outline" className="text-xs">
                      5,241 Observations
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      842 Trading Samples
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      12h Since Last Update
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
            
            <ScrollArea className="h-96 rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Observation</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Outcome</TableHead>
                    <TableHead>Learning</TableHead>
                    <TableHead className="text-right">Impact</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {learningData.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-mono text-xs">
                        {item.timestamp}
                      </TableCell>
                      <TableCell className="max-w-[200px] truncate">
                        {item.observation}
                      </TableCell>
                      <TableCell className="text-xs">
                        {item.action}
                      </TableCell>
                      <TableCell>
                        <span className={`px-2 py-0.5 rounded text-xs ${
                          item.outcome.includes('Profit') 
                            ? 'bg-success/20 text-success' 
                            : item.outcome.includes('Loss avoided')
                              ? 'bg-warning/20 text-warning'
                              : 'bg-destructive/20 text-destructive'
                        }`}>
                          {item.outcome}
                        </span>
                      </TableCell>
                      <TableCell className="max-w-[200px] truncate text-xs">
                        {item.learningOutcome}
                      </TableCell>
                      <TableCell className="text-right">
                        <span className={`inline-flex items-center ${
                          item.confidenceChange > 0 
                            ? 'text-success' 
                            : 'text-destructive'
                        }`}>
                          {item.confidenceChange > 0 ? '+' : ''}{item.confidenceChange}%
                          {item.confidenceChange > 0 
                            ? <ArrowUpRight className="ml-0.5 w-3 h-3" />
                            : <AlertCircle className="ml-0.5 w-3 h-3" />
                          }
                        </span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </ScrollArea>
          </TabsContent>
          
          <TabsContent value="database">
            <div className="p-4 text-center border rounded-md bg-muted/30">
              <Database className="w-10 h-10 mx-auto mb-2 text-muted-foreground" />
              <h3 className="text-lg font-medium">Knowledge Database (RAG)</h3>
              <p className="text-sm text-muted-foreground mt-1 mb-4 max-w-lg mx-auto">
                The AI agent stores observations, patterns, and trading outcomes in a vector database to improve its decision making over time.
              </p>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4 text-left">
                <div className="border p-3 rounded-md">
                  <h4 className="text-sm font-medium">Pattern Recognition</h4>
                  <div className="text-2xl font-bold mt-1">2,458</div>
                  <p className="text-xs text-muted-foreground">Stored patterns</p>
                </div>
                
                <div className="border p-3 rounded-md">
                  <h4 className="text-sm font-medium">Token Analysis</h4>
                  <div className="text-2xl font-bold mt-1">15,723</div>
                  <p className="text-xs text-muted-foreground">Unique tokens</p>
                </div>
                
                <div className="border p-3 rounded-md">
                  <h4 className="text-sm font-medium">Trading Outcomes</h4>
                  <div className="text-2xl font-bold mt-1">842</div>
                  <p className="text-xs text-muted-foreground">Completed trades</p>
                </div>
                
                <div className="border p-3 rounded-md">
                  <h4 className="text-sm font-medium">Vector Embeddings</h4>
                  <div className="text-2xl font-bold mt-1">45.2GB</div>
                  <p className="text-xs text-muted-foreground">Database size</p>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AILearningSystem;
