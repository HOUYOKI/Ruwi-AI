import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useState } from "react";
import GalleryPage from "./pages/GalleryPage";
import ArtifactPage from "./pages/ArtifactPage";
import IdentifyPage from "./pages/IdentifyPage";
import ThemeToggle from "./components/ThemeToggle";
import LanguageToggle from "./components/LanguageToggle";

function App() {
  const [visitId] = useState(() => crypto.randomUUID());

  return (
    <BrowserRouter>
      <div className="fixed end-4 top-4 z-50 flex items-center gap-2">
        <LanguageToggle />
        <ThemeToggle />
      </div>
      <div className="min-h-screen font-body text-text">
        <Routes>
          <Route path="/" element={<GalleryPage />} />
          <Route
            path="/experience/:id"
            element={<ArtifactPage visitId={visitId} />}
          />
          <Route path="/identify" element={<IdentifyPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
