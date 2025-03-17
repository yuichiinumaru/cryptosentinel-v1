
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from '@/components/ui/use-toast';
import { Badge } from '@/components/ui/badge';
import { Loader2, Check, X } from 'lucide-react';
import { api, getApiUrl, setApiUrl } from '@/services/api';

const ApiConfigSection = () => {
  const [apiUrl, setApiUrlState] = useState(getApiUrl());
  const [openaiKey, setOpenaiKey] = useState(localStorage.getItem('openaiApiKey') || '');
  const [openaiEndpoint, setOpenaiEndpoint] = useState(localStorage.getItem('openaiEndpoint') || '');
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'untested' | 'success' | 'failed'>('untested');
  
  const saveApiConfig = async () => {
    try {
      // Save API URL
      setApiUrl(apiUrl);
      
      // Save OpenAI API key & endpoint to localStorage
      localStorage.setItem('openaiApiKey', openaiKey);
      if (openaiEndpoint) {
        localStorage.setItem('openaiEndpoint', openaiEndpoint);
      } else {
        localStorage.removeItem('openaiEndpoint');
      }
      
      // Send to backend if connected
      if (connectionStatus === 'success') {
        await api.config.updateOpenAI(openaiKey, openaiEndpoint);
      }
      
      toast({
        title: "Settings Saved",
        description: "API configuration has been updated",
      });
    } catch (error) {
      console.error('Failed to save API config:', error);
      toast({
        title: "Save Failed",
        description: "Could not save API configuration",
        variant: "destructive",
      });
    }
  };
  
  const testConnection = async () => {
    setIsTestingConnection(true);
    setConnectionStatus('untested');
    
    try {
      // First save the URL so the test uses the current value
      setApiUrl(apiUrl);
      
      const isConnected = await api.testConnection();
      setConnectionStatus(isConnected ? 'success' : 'failed');
      
      toast({
        title: isConnected ? "Connection Successful" : "Connection Failed",
        description: isConnected 
          ? "Successfully connected to the backend API" 
          : "Could not connect to the backend. Please check the URL and try again.",
        variant: isConnected ? "default" : "destructive",
      });
    } catch (error) {
      setConnectionStatus('failed');
      toast({
        title: "Connection Failed",
        description: "Could not connect to the backend API",
        variant: "destructive",
      });
    } finally {
      setIsTestingConnection(false);
    }
  };
  
  useEffect(() => {
    // Test connection on component mount
    testConnection();
  }, []);
  
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-medium mb-4">API Configuration</h3>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label htmlFor="api-url">Backend API URL</Label>
              <Badge variant={connectionStatus === 'success' ? 'success' : connectionStatus === 'failed' ? 'destructive' : 'outline'}>
                {connectionStatus === 'success' ? (
                  <><Check className="h-3 w-3 mr-1" /> Connected</>
                ) : connectionStatus === 'failed' ? (
                  <><X className="h-3 w-3 mr-1" /> Disconnected</>
                ) : (
                  'Not Tested'
                )}
              </Badge>
            </div>
            <div className="flex space-x-2">
              <Input 
                id="api-url" 
                placeholder="http://localhost:5000" 
                value={apiUrl}
                onChange={(e) => setApiUrlState(e.target.value)}
              />
              <Button 
                onClick={testConnection} 
                variant="outline" 
                disabled={isTestingConnection}
              >
                {isTestingConnection ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Testing</>
                ) : (
                  'Test'
                )}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              The URL of your Python backend API
            </p>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="openai-key">OpenAI API Key</Label>
            <Input 
              id="openai-key" 
              type="password"
              placeholder="sk-..." 
              value={openaiKey}
              onChange={(e) => setOpenaiKey(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              Required for AI agent functionality
            </p>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="openai-endpoint">OpenAI Custom Endpoint (Optional)</Label>
            <Input 
              id="openai-endpoint" 
              placeholder="https://api.openai.com/v1" 
              value={openaiEndpoint}
              onChange={(e) => setOpenaiEndpoint(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              Alternative endpoint for OpenAI API compatible services
            </p>
          </div>
          
          <Button onClick={saveApiConfig} className="w-full">
            Save API Configuration
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ApiConfigSection;
