
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/analytics" element={<Navigate to="/" replace state={{ tab: "analytics" }} />} />
          <Route path="/trading" element={<Navigate to="/" replace state={{ tab: "trading" }} />} />
          <Route path="/agents" element={<Navigate to="/" replace state={{ tab: "agents" }} />} />
          <Route path="/wallet" element={<Navigate to="/" replace state={{ tab: "wallet" }} />} />
          <Route path="/security" element={<Navigate to="/" replace state={{ tab: "security" }} />} />
          <Route path="/settings" element={<Navigate to="/" replace state={{ tab: "settings" }} />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
