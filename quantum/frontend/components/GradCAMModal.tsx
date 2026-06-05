import React, { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, X } from "lucide-react";
import { motion } from "framer-motion";

interface GradCAMModalProps {
  isOpen: boolean;
  onClose: () => void;
  classCode: string;
  className: string;
}

export const GradCAMModal: React.FC<GradCAMModalProps> = ({
  isOpen,
  onClose,
  classCode,
  className,
}) => {
  const [currentExample, setCurrentExample] = useState(0);
  const [zoom, setZoom] = useState(1);
  const totalExamples = 4;

  const imagePath = `/grad_cam_example_${classCode}_${currentExample}.webp`;

  const handlePrevious = () => {
    setCurrentExample((prev) => (prev === 0 ? totalExamples - 1 : prev - 1));
    setZoom(1);
  };

  const handleNext = () => {
    setCurrentExample((prev) => (prev === totalExamples - 1 ? 0 : prev + 1));
    setZoom(1);
  };

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(prev + 0.2, 3));
  };

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(prev - 0.2, 1));
  };

  const handleReset = () => {
    setZoom(1);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] bg-slate-900 border-cyan-500/30 overflow-auto">
        <DialogHeader className="border-b border-cyan-500/20 pb-4">
          <div className="flex items-center justify-between w-full">
            <DialogTitle className="text-cyan-400 text-lg">
              {className} - Grad-CAM Gallery
            </DialogTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="text-cyan-400 hover:text-cyan-300"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </DialogHeader>

        <div className="space-y-6 py-6">
          {/* Main Image Viewer */}
          <div className="flex flex-col items-center gap-4">
            {/* Image Container with Zoom */}
            <motion.div
              className="relative w-full max-w-4xl bg-slate-800/50 rounded-lg border border-cyan-500/20 overflow-hidden"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <div className="flex items-center justify-center p-4 min-h-[400px]">
                <div
                  className="relative overflow-auto max-h-[500px] max-w-full"
                  style={{
                    transform: `scale(${zoom})`,
                    transformOrigin: "center",
                    transition: "transform 0.2s ease-in-out",
                  }}
                >
                  <img
                    src={imagePath}
                    alt={`Grad-CAM example ${currentExample + 1}`}
                    className="w-full rounded-lg"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src =
                        "/grad_cam_professional_" + classCode + ".webp";
                    }}
                  />
                </div>
              </div>

              {/* Zoom Info */}
              <div className="absolute top-4 right-4 bg-slate-900/80 px-3 py-2 rounded border border-cyan-500/30 text-xs text-cyan-400">
                Zoom: {(zoom * 100).toFixed(0)}%
              </div>
            </motion.div>

            {/* Zoom Controls */}
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleZoomOut}
                disabled={zoom <= 1}
                className="border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
              >
                <ZoomOut className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleReset}
                className="border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
              >
                Reset
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleZoomIn}
                disabled={zoom >= 3}
                className="border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
              >
                <ZoomIn className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Navigation and Example Selector */}
          <div className="flex items-center justify-between gap-4 bg-slate-800/30 p-4 rounded-lg border border-cyan-500/20">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrevious}
              className="border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
            >
              <ChevronLeft className="w-4 h-4 mr-2" />
              Previous
            </Button>

            {/* Example Selector */}
            <div className="flex gap-2">
              {Array.from({ length: totalExamples }).map((_, idx) => (
                <motion.button
                  key={idx}
                  onClick={() => {
                    setCurrentExample(idx);
                    setZoom(1);
                  }}
                  className={`w-10 h-10 rounded border transition-all ${
                    currentExample === idx
                      ? "bg-cyan-500/30 border-cyan-400 text-cyan-400"
                      : "bg-slate-700/30 border-cyan-500/20 text-gray-400 hover:border-cyan-400/50"
                  }`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {idx + 1}
                </motion.button>
              ))}
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={handleNext}
              className="border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
            >
              Next
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          </div>

          {/* Info Section */}
          <div className="bg-slate-800/30 p-4 rounded-lg border border-cyan-500/20">
            <p className="text-sm text-gray-400">
              <span className="text-cyan-400 font-semibold">Example {currentExample + 1} of {totalExamples}</span>
              {" "}- Explore different Grad-CAM visualizations for {className}. Use zoom controls to examine specific regions of interest. The heatmap shows areas that influenced the model's classification decision.
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
