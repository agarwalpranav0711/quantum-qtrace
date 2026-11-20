import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import { CommandCenterPage } from "./pages/CommandCenterPage";
import { InvestigationsPage } from "./pages/InvestigationsPage";
import { CreateInvestigationPage } from "./pages/CreateInvestigationPage";
import { InvestigationDetailPage } from "./pages/InvestigationDetailPage";
import { EvidenceLibraryPage } from "./pages/EvidenceLibraryPage";
import { EvidenceDetailPage } from "./pages/EvidenceDetailPage";
import { EvidenceUploadPage } from "./pages/EvidenceUploadPage";
import { AnalysisWorkspacePage } from "./pages/AnalysisWorkspacePage";
import { ForensicCanvasPage } from "./pages/ForensicCanvasPage";
import { QuantumLabPage } from "./pages/QuantumLabPage";
import { FindingsPage } from "./pages/FindingsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { SettingsPage } from "./pages/SettingsPage";

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<CommandCenterPage />} />
          <Route path="/investigations" element={<InvestigationsPage />} />
          <Route path="/investigations/new" element={<CreateInvestigationPage />} />
          <Route path="/investigations/:caseId" element={<InvestigationDetailPage />} />
          <Route path="/evidence" element={<EvidenceLibraryPage />} />
          <Route path="/evidence/upload" element={<EvidenceUploadPage />} />
          <Route path="/evidence/:evidenceId" element={<EvidenceDetailPage />} />
          <Route path="/analysis" element={<AnalysisWorkspacePage />} />
          <Route path="/canvas" element={<ForensicCanvasPage />} />
          <Route path="/quantum-lab" element={<QuantumLabPage />} />
          <Route path="/findings" element={<FindingsPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;

