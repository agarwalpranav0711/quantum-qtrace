import React, { useState, useEffect } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { api } from "../../services/api";

export const AppShell: React.FC = () => {
  const [isHealthy, setIsHealthy] = useState<boolean>(true);
  const [version, setVersion] = useState<string>("0.4.0");

  useEffect(() => {
    let isMounted = true;

    const checkHealth = async () => {
      try {
        const res = await api.getHealth();
        if (isMounted) {
          setIsHealthy(res.status === "healthy");
          if (res.version) setVersion(res.version);
        }
      } catch {
        if (isMounted) {
          setIsHealthy(false);
        }
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-dark-950 text-slate-100 font-sans">
      {/* Workstation Sidebar */}
      <Sidebar isHealthy={isHealthy} version={version} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 bg-dark-950/90">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

