
import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import AgentActivityMonitor from "./AgentActivityMonitor";
import ConfigPanel from "./ConfigPanel";
import FundsDashboard from "./FundsDashboard";
import TechnicalAnalysisConfig from "./TechnicalAnalysisConfig";
import PriceChart from "./PriceChart";
import TradeList from "./TradeList";
import StatusIndicator from "./StatusIndicator";
import AgentTeam from "./AgentTeam";
import BlacklistManager from "./BlacklistManager";
import AILearningSystem from "./AILearningSystem";
import ChatWithAgent from "./ChatWithAgent";
import WalletConnection from "./WalletConnection";

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState("dashboard");

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">CryptoSentinel Dashboard</h1>
      
      <StatusIndicator status="online" />
      
      <Tabs defaultValue={activeTab} value={activeTab} onValueChange={setActiveTab} className="mt-6">
        <TabsList className="grid grid-cols-4 md:grid-cols-7 mb-8">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="trading">Trading</TabsTrigger>
          <TabsTrigger value="agents">Agents</TabsTrigger>
          <TabsTrigger value="wallet">Wallet</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>
        
        <TabsContent value="dashboard" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <FundsDashboard />
            <AgentActivityMonitor />
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <PriceChart />
            <TradeList />
          </div>
        </TabsContent>
        
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <PriceChart />
            <TechnicalAnalysisConfig />
          </div>
        </TabsContent>
        
        <TabsContent value="trading" className="space-y-4">
          <div className="grid grid-cols-1 gap-4">
            <TradeList />
            <ConfigPanel />
          </div>
        </TabsContent>
        
        <TabsContent value="agents" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <AgentTeam />
            <AgentActivityMonitor />
          </div>
          <div className="grid grid-cols-1 gap-4">
            <ChatWithAgent />
          </div>
        </TabsContent>
        
        <TabsContent value="wallet" className="space-y-4">
          <div className="grid grid-cols-1 gap-4">
            <WalletConnection />
            <FundsDashboard />
          </div>
        </TabsContent>
        
        <TabsContent value="security" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <BlacklistManager />
            <AILearningSystem />
          </div>
        </TabsContent>
        
        <TabsContent value="settings" className="space-y-4">
          <div className="grid grid-cols-1 gap-4">
            <ConfigPanel />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Dashboard;
