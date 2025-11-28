import React from "react";
import type { Story } from "../types";
import { motion } from "framer-motion";
import { User, Heart } from "lucide-react";
import "./StoryCard.css";

interface StoryCardProps {
  story: Story;
  onClick?: () => void;
  compact?: boolean;
}

export const StoryCard: React.FC<StoryCardProps> = ({
  story,
  onClick,
  compact = false,
}) => {
  // Images hidden as per user request
  // const thumbnail =
  //   Array.isArray(story.photos) && story.photos.length > 0
  //     ? `http://localhost:8000/${story.photos[0].file_path.replace(/\\/g, "/")}`
  //     : null;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      className={`story-card ${story.used_in_presentation ? "used" : ""}`}
      onClick={onClick}
    >
      {/* Image display removed */}
      {/* {thumbnail && (
        <div className="story-card-image">
          <img src={thumbnail} alt={story.title} />
        </div>
      )} */}
      <div className="story-card-content">
        <h3 className="story-card-title">{story.title}</h3>

        <div className="story-card-meta">
          <div className="meta-item">
            <User size={16} className="icon-blue" />
            <span>{story.person}</span>
          </div>
          <div className="meta-item">
            <Heart size={16} className="icon-pink" />
            <span>{story.emotion}</span>
          </div>

        </div>

        {story.used_in_presentation && (
          <div className="presented-badge">Presented</div>
        )}
      </div>
    </motion.div>
  );
};
