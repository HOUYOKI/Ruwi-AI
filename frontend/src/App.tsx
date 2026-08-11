import { BrowserRouter, Routes, Route } from "react-router-dom";
import GalleryPage from "./pages/GalleryPage";
import ArtifactPage from "./pages/ArtifactPage";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-neutral-950 text-neutral-100">
        <Routes>
          <Route path="/" element={<GalleryPage />} />
          <Route path="/artifacts/:id" element={<ArtifactPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
