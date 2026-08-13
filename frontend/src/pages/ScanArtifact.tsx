import { useRef, useState, useCallback } from "react";
import Webcam from "react-webcam";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const videoConstraints = {
  width: 720,
  height: 720,
  facingMode: "environment", 
};

export default function ScanArtifact() {
  const webcamRef = useRef<Webcam>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      setCapturedImage(imageSrc);
      setError(null);
    }
  }, [webcamRef]);

  const retake = () => {
    setCapturedImage(null);
    setError(null);
  };

  // to backend to analyseeeeeee
  const analyzeImage = async () => {
    if (!capturedImage) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const base64Data = capturedImage.split(",")[1];

      const response = await fetch(`${API_BASE_URL}/identify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_base64: base64Data }),
      });

      if (!response.ok) {
        throw new Error("خطا مره اخرى");
      }

      const data = await response.json();

      if (data.artifact_id) {
        navigate(`/artifacts/${data.artifact_id}`);
      } else {
        setError("اذا مافي القطعه");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "صار خطا");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div style={{ maxWidth: 480, margin: "0 auto", padding: 24, textAlign: "center" }}>
      <h2>صور القطعة الاثرية</h2>

      <div
        style={{
          borderRadius: 12,
          overflow: "hidden",
          marginBottom: 16,
          backgroundColor: "#000",
        }}
      >
        {!capturedImage ? (
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            videoConstraints={videoConstraints}
            style={{ width: "100%", display: "block" }}
          />
        ) : (
          <img src={capturedImage} alt="القطعة الملتقطة" style={{ width: "100%", display: "block" }} />
        )}
      </div>

      {error && (
        <p style={{ color: "#e74c3c", marginBottom: 12 }}>{error}</p>
      )}

      {!capturedImage ? (
        <button onClick={capture} style={buttonStyle}>
           التقط الصورة
        </button>
      ) : (
        <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
          <button onClick={retake} style={{ ...buttonStyle, backgroundColor: "#555" }}>
            مره اخرى 
          </button>
          <button onClick={analyzeImage} disabled={isAnalyzing} style={buttonStyle}>
            {isAnalyzing ? "جاري التحليل..." : "✓ تحليل القطعة"}
          </button>
        </div>
      )}
    </div>
  );
}

const buttonStyle: React.CSSProperties = {
  padding: "12px 24px",
  borderRadius: 8,
  border: "none",
  backgroundColor: "#c9a15a",
  color: "#000",
  fontWeight: 600,
  cursor: "pointer",
  fontSize: 16,
};
