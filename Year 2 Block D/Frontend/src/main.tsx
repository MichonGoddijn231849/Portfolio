import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import { UploadProvider } from "@/context/UploadContext"; // <-- Import your new context

createRoot(document.getElementById("root")!).render(
  <UploadProvider>  {/* <-- Wrap your App */}
    <App />
  </UploadProvider>
);


