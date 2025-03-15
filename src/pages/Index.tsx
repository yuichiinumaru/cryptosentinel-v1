
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Layout from '@/components/Layout';
import Dashboard from '@/components/Dashboard';

const Index = () => {
  const location = useLocation();
  const state = location.state as { tab?: string } | null;
  
  // Pass tab from route state to dashboard
  useEffect(() => {
    // This will be used by Dashboard component to set the active tab
    console.log("Tab from route state:", state?.tab);
  }, [state]);
  
  return (
    <Layout>
      <div className="container py-6 px-4 md:px-6">
        <Dashboard initialTab={state?.tab} />
      </div>
    </Layout>
  );
};

export default Index;
