import React from "react";
import type { Photo, AlbumLayout } from "../types";
import "./AlbumLayoutPreview.css";

interface AlbumLayoutPreviewProps {
  layoutJson: string;
  photos: Photo[];
}

export const AlbumLayoutPreview: React.FC<AlbumLayoutPreviewProps> = ({
  layoutJson,
  photos,
}) => {
  let layout: AlbumLayout | null = null;

  try {
    layout = JSON.parse(layoutJson) as AlbumLayout;
  } catch (error) {
    console.error("Failed to parse album layout JSON", error);
    return (
      <div className="album-layout-preview">
        <div className="layout-error">Invalid album layout JSON</div>
      </div>
    );
  }

  if (!layout) {
    return null;
  }

  // Map photo_id to actual photo URLs
  const getPhotoUrl = (photoId: string | number): string | null => {
    const index = typeof photoId === "string" ? parseInt(photoId, 10) : photoId;
    if (index >= 0 && index < photos.length) {
      return `http://localhost:8000/${photos[index].file_path.replace(/\\/g, "/")}`;
    }
    return null;
  };

  return (
    <div className="album-layout-preview">
      <div className="layout-header">
        <h3 className="layout-title">{layout.page_title}</h3>
        <p className="layout-description">{layout.page_description}</p>
      </div>

      <div className="layout-grid">
        {layout.photos.map((photo, idx) => {
          const photoUrl = getPhotoUrl(photo.photo_id);
          if (!photoUrl) {
            return (
              <div
                key={idx}
                className={`layout-photo layout-photo-${photo.role}`}
              >
                <div className="photo-missing">Photo not found</div>
                <p className="photo-caption">{photo.caption}</p>
              </div>
            );
          }

          return (
            <div
              key={idx}
              className={`layout-photo layout-photo-${photo.role}`}
            >
              <img src={photoUrl} alt={photo.caption} />
              <p className="photo-caption">{photo.caption}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
