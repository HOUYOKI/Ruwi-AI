import { BrowserRouter, Routes, Route } from "react-router-dom";
import GalleryPage from "./pages/GalleryPage";
import ArtifactPage from "./pages/ArtifactPage";
import ThemeToggle from "./components/ThemeToggle";
import LanguageToggle from "./components/LanguageToggle";

function App() {
  return (
    <BrowserRouter>
      <div className="fixed top-4 right-4 z-50 flex items-center gap-2">
        <LanguageToggle />
        <ThemeToggle />
      </div>
      <div className="min-h-screen font-body text-text">
        <Routes>
          <Route path="/" element={<GalleryPage />} />
          <Route path="/artifacts/:id" element={<ArtifactPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
