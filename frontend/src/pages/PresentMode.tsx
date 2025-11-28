import React, { useState, useEffect } from "react";
import { getStories, markStoryUsed, resetStories } from "../api";
import type { Story } from "../types";
import { StoryCard } from "../components/StoryCard";
import { AlbumLayoutPreview } from "../components/AlbumLayoutPreview";
import { AnimatePresence, motion } from "framer-motion";
import { X, RefreshCw } from "lucide-react";
import "./PresentMode.css";

export const PresentMode: React.FC = () => {
  useEffect(() => {
    console.log("PresentMode mounted");
  }, []);
  const [stories, setStories] = useState<Story[]>([]);
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  const [isResetting, setIsResetting] = useState(false);

  useEffect(() => {
    loadStories();
  }, []);

  const loadStories = async () => {
    const data = await getStories();
    setStories(data);
  };

  const hasPresentedStories = () => stories.some((s) => s.used_in_presentation);

  const handleSelectStory = (story: Story) => {
    setSelectedStory(story);
    // Mark as used
    if (!story.used_in_presentation) {
      markStoryUsed(story.id);
      // Update local state
      setStories((prev) =>
        prev.map((s) =>
          s.id === story.id ? { ...s, used_in_presentation: true } : s
        )
      );
    }
  };

  const handleClose = () => {
    setSelectedStory(null);
  };

  return (
    <div className="present-mode-container">
      <AnimatePresence>
        {!selectedStory ? (
          <motion.div
            className="grid-view"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="present-header">
              <h1 className="present-title">Select a Story</h1>
              <div className="present-actions">
                <button
                  aria-label="Reset all presented stories"
                  className="reset-all-btn"
                  onClick={async () => {
                    const confirmed = window.confirm(
                      "Reset all presented statuses? This will mark all stories as not presented. Continue?"
                    );
                    if (!confirmed) return;
                    try {
                      setIsResetting(true);
                      await resetStories();
                      await loadStories();
                    } catch (err) {
                      console.error("Failed to reset stories", err);
                      alert(
                        "Failed to reset stories. See console for details."
                      );
                    } finally {
                      setIsResetting(false);
                    }
                  }}
                  disabled={isResetting || !hasPresentedStories()}
                >
                  <RefreshCw size={16} />
                  {isResetting ? " Resetting..." : " Reset All"}
                </button>
              </div>
            </div>
            <div className="stories-grid">
              {stories.map((story) => (
                <StoryCard
                  key={story.id}
                  story={story}
                  onClick={() => handleSelectStory(story)}
                />
              ))}
            </div>
          </motion.div>
        ) : (
          <motion.div
            className="presentation-view"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
          >
            <button className="close-btn" onClick={handleClose}>
              <X size={32} />
            </button>

            {/* Album Layout */}
            {selectedStory.album_json && (
              <div className="album-layout">
                <AlbumLayoutPreview
                  layoutJson={selectedStory.album_json}
                  photos={selectedStory.photos}
                />
              </div>
            )}

            {/* Audio Player */}
            {selectedStory.audio_file_path && (
              <div className="audio-controls">
                <audio
                  controls
                  src={`http://localhost:8000/${selectedStory.audio_file_path.replace(
                    /\\/g,
                    "/"
                  )}`}
                  className="audio-player"
                >
                  Your browser does not support the audio element.
                </audio>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
