import React, { useState, useEffect } from "react";
import {
  createStory,
  getStories,
  updateStory,
  deleteStory,
  addPhotosToStory,
  deletePhoto,
  regenerateTranscript,
  regenerateAudio,
} from "../api";
import type { Story, StoryCreate } from "../types";
import { StoryCard } from "../components/StoryCard";
import { AlbumLayoutPreview } from "../components/AlbumLayoutPreview";
import {
  Plus,
  Upload,
  Loader2,
  Save,
  X,
  Trash2,
  AlertTriangle,
  RefreshCw,
} from "lucide-react";
import "./EditMode.css";

export const EditMode: React.FC = () => {
  useEffect(() => {
    console.log("EditMode mounted");
  }, []);
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);

  const [formData, setFormData] = useState<StoryCreate>({
    title: "",
    person: "",
    emotion: "",
    notes: "",
    files: [],
  });
  const [speech, setSpeech] = useState("");
  const [voiceDirection, setVoiceDirection] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [photosToAdd, setPhotosToAdd] = useState<File[]>([]);
  const [regeneratingTranscript, setRegeneratingTranscript] = useState(false);
  const [regeneratingAudio, setRegeneratingAudio] = useState(false);

  useEffect(() => {
    loadStories();
  }, []);

  const loadStories = async () => {
    try {
      const data = await getStories();
      setStories(data);
    } catch (error) {
      console.error("Failed to load stories", error);
    }
  };

  const handleSelectStory = (story: Story) => {
    setSelectedStory(story);
    setFormData({
      title: story.title,
      person: story.person,
      emotion: story.emotion,
      notes: story.notes,
      files: [], // Files cannot be pre-filled easily
    });
    setSpeech(story.generated_speech || "");
    setVoiceDirection(story.generated_voice_direction || "");
  };

  const handleCancelEdit = () => {
    setSelectedStory(null);
    setFormData({
      title: "",
      person: "",
      emotion: "",
      notes: "",
      files: [],
    });
    setSpeech("");
    setVoiceDirection("");
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSpeechChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setSpeech(e.target.value);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFormData((prev) => ({
        ...prev,
        files: Array.from(e.target.files || []),
      }));
    }
  };

  const handleAddPhotos = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setPhotosToAdd(Array.from(e.target.files));
    }
  };

  const handleUploadNewPhotos = async () => {
    if (!selectedStory || photosToAdd.length === 0) return;
    setLoading(true);
    try {
      await addPhotosToStory(selectedStory.id, photosToAdd);
      await loadStories();
      // Update selected story with new photos
      const updated = (await getStories()).find(
        (s) => s.id === selectedStory.id
      );
      if (updated) setSelectedStory(updated);
      setPhotosToAdd([]);
    } catch (error) {
      console.error("Failed to upload photos", error);
      alert("Failed to upload photos");
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveExistingPhoto = async (photoId: number) => {
    if (!selectedStory) return;
    const confirmed = window.confirm("Remove this photo from the story?");
    if (!confirmed) return;
    setLoading(true);
    try {
      await deletePhoto(photoId);
      await loadStories();
      const updated = (await getStories()).find(
        (s) => s.id === selectedStory.id
      );
      if (updated) setSelectedStory(updated);
    } catch (error) {
      console.error("Failed to delete photo", error);
      alert("Failed to delete photo");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (selectedStory) {
        // Update existing story
        await updateStory(selectedStory.id, {
          title: formData.title,
          person: formData.person,
          emotion: formData.emotion,
          notes: formData.notes,
          generated_speech: speech,
        });
        // Upload any new photos if selected
        if (photosToAdd.length > 0) {
          await addPhotosToStory(selectedStory.id, photosToAdd);
          setPhotosToAdd([]);
        }
      } else {
        // Create new story
        await createStory(formData);
      }

      await loadStories();
      if (!selectedStory) {
        setFormData({
          title: "",
          person: "",
          emotion: "",
          notes: "",
          files: [],
        });
      }
    } catch (error) {
      console.error("Failed to save story", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();
    console.log("Delete button clicked, showing confirmation");
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (!selectedStory) return;

    setShowDeleteConfirm(false);
    setLoading(true);
    try {
      console.log("Deleting story with ID:", selectedStory.id);
      await deleteStory(selectedStory.id);
      console.log("Delete successful");
      await loadStories();
      handleCancelEdit();
    } catch (error) {
      console.error("Failed to delete story", error);
      alert("Failed to delete story. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const cancelDelete = () => {
    setShowDeleteConfirm(false);
  };

  const handleRegenerateTranscript = async () => {
    if (!selectedStory) return;
    setRegeneratingTranscript(true);
    try {
      const { generated_speech, generated_voice_direction } = await regenerateTranscript(selectedStory.id);
      setSpeech(generated_speech);
      setVoiceDirection(generated_voice_direction);

      await loadStories();
      const updated = (await getStories()).find((s) => s.id === selectedStory.id);
      if (updated) setSelectedStory(updated);
    } catch (error) {
      console.error("Failed to regenerate transcript", error);
      alert("Failed to regenerate transcript. Please try again.");
    } finally {
      setRegeneratingTranscript(false);
    }
  };

  const handleRegenerateAudio = async () => {
    if (!selectedStory) return;
    setRegeneratingAudio(true);
    try {
      await regenerateAudio(selectedStory.id, speech);
      await loadStories();
      const updated = (await getStories()).find((s) => s.id === selectedStory.id);
      if (updated) setSelectedStory(updated);
    } catch (error) {
      console.error("Failed to regenerate audio", error);
      alert("Failed to regenerate audio. Please try again.");
    } finally {
      setRegeneratingAudio(false);
    }
  };

  return (
    <div className="edit-mode-container">
      <div className="sidebar">
        <div className="sidebar-header">
          <h2 className="sidebar-title">Stories</h2>
          <button className="new-story-btn" onClick={handleCancelEdit}>
            <Plus size={20} />
          </button>
        </div>
        <div className="story-list">
          {stories.map((story) => (
            <StoryCard
              key={story.id}
              story={story}
              compact
              onClick={() => handleSelectStory(story)}
            />
          ))}
        </div>
      </div>

      <div className="main-content">
        <div className="main-header">
          <h1 className="page-title">
            {selectedStory ? "Edit Story" : "Create New Story"}
          </h1>
          {selectedStory && (
            <div className="header-actions">
              <button
                type="button"
                className="delete-btn"
                onClick={handleDelete}
                disabled={loading}
                title="Delete story"
              >
                <Trash2 size={20} />
              </button>
              <button
                type="button"
                className="cancel-btn"
                onClick={handleCancelEdit}
              >
                <X size={20} /> Cancel
              </button>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="create-form">
          <div className="form-group">
            <label>Title</label>
            <input
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Person/People</label>
              <input
                name="person"
                value={formData.person}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Emotion</label>
              <input
                name="emotion"
                value={formData.emotion}
                onChange={handleInputChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Description / Notes</label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              rows={4}
              required
            />
          </div>

          {selectedStory && (
            <div className="form-group">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                <label>Generated Speech</label>
                <div style={{ display: "flex", gap: "8px" }}>
                  <button
                    type="button"
                    className="regenerate-speech-btn"
                    onClick={handleRegenerateTranscript}
                    disabled={regeneratingTranscript || loading}
                    title="Regenerate transcript using AI"
                  >
                    {regeneratingTranscript ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <RefreshCw size={16} />
                    )}
                    {regeneratingTranscript ? "Regenerating..." : "Regenerate Transcript"}
                  </button>
                  <button
                    type="button"
                    className="regenerate-speech-btn"
                    onClick={handleRegenerateAudio}
                    disabled={regeneratingAudio || loading}
                    title="Regenerate audio from current transcript"
                  >
                    {regeneratingAudio ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <RefreshCw size={16} />
                    )}
                    {regeneratingAudio ? "Regenerating..." : "Regenerate Audio"}
                  </button>
                </div>
              </div>
              <div className="voice-direction-display" style={{ marginBottom: "10px", fontStyle: "italic", color: "#ffd700" }}>
                {voiceDirection}
              </div>
              <textarea
                name="speech"
                value={speech}
                onChange={handleSpeechChange}
                rows={10}
                className="speech-editor"
              />

              {/* Audio Preview */}
              {selectedStory.audio_file_path && (
                <div className="audio-preview">
                  <label>Audio Preview</label>
                  <audio
                    controls
                    src={`http://localhost:8000/${selectedStory.audio_file_path.replace(
                      /\\/g,
                      "/"
                    )}`}
                    className="audio-player-edit"
                  >
                    Your browser does not support the audio element.
                  </audio>
                </div>
              )}

              {/* Album Layout */}
              {selectedStory.album_json && (
                <div className="album-json-section" style={{ marginTop: "20px" }}>
                  <label>Album Layout</label>
                  <div style={{ marginTop: "10px" }}>
                    <div style={{ marginBottom: "20px" }}>
                      <h4 style={{
                        fontSize: "14px",
                        color: "#ffd700",
                        marginBottom: "8px",
                        fontWeight: "500"
                      }}>Raw JSON Output</h4>
                      <pre style={{
                        background: "#1a1a1a",
                        padding: "10px",
                        borderRadius: "4px",
                        overflowX: "auto",
                        color: "#a0a0a0",
                        fontSize: "12px",
                        maxHeight: "200px",
                        margin: 0
                      }}>
                        {selectedStory.album_json}
                      </pre>
                    </div>
                    <div>
                      <h4 style={{
                        fontSize: "14px",
                        color: "#ffd700",
                        marginBottom: "8px",
                        fontWeight: "500"
                      }}>Visual Preview</h4>
                      <AlbumLayoutPreview
                        layoutJson={selectedStory.album_json}
                        photos={selectedStory.photos}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {selectedStory && (
            <div className="form-group">
              <label>Photos</label>

              {selectedStory.photos && selectedStory.photos.length > 0 && (
                <div className="existing-photos">
                  {selectedStory.photos.map((photo) => (
                    <div key={photo.id} className="photo-item">
                      <img
                        src={`http://localhost:8000/${photo.file_path.replace(
                          /\\/g,
                          "/"
                        )}`}
                        alt="Story photo"
                      />
                      <button
                        type="button"
                        className="remove-photo-btn"
                        onClick={() => handleRemoveExistingPhoto(photo.id)}
                        title="Remove photo"
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <div className="add-photos-section">
                <div className="file-upload">
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleAddPhotos}
                    id="add-photos-input"
                  />
                  <label htmlFor="add-photos-input" className="file-label">
                    <Upload size={20} />
                    <span>
                      {photosToAdd.length > 0
                        ? `${photosToAdd.length} files selected`
                        : "Add More Photos"}
                    </span>
                  </label>
                </div>
                {photosToAdd.length > 0 && (
                  <button
                    type="button"
                    className="upload-photos-btn"
                    onClick={handleUploadNewPhotos}
                    disabled={loading}
                  >
                    <Upload size={16} />
                    Upload Selected
                  </button>
                )}
              </div>
            </div>
          )}

          {!selectedStory && (
            <div className="form-group">
              <label>Photos (Max 4)</label>
              <div className="file-upload">
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleFileChange}
                  id="file-input"
                />
                <label htmlFor="file-input" className="file-label">
                  <Upload size={20} />
                  <span>
                    {formData.files.length > 0
                      ? `${formData.files.length} files selected`
                      : "Upload Photos"}
                  </span>
                </label>
              </div>
            </div>
          )}

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? (
              <Loader2 className="animate-spin" />
            ) : selectedStory ? (
              <Save />
            ) : (
              <Plus />
            )}
            <span>
              {loading
                ? "Saving..."
                : selectedStory
                  ? "Save Changes"
                  : "Create Story"}
            </span>
          </button>
        </form>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && selectedStory && (
        <div className="modal-overlay" onClick={cancelDelete}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <AlertTriangle size={48} className="warning-icon" />
              <h2>Delete Story?</h2>
            </div>
            <p className="modal-message">
              Are you sure you want to delete "
              <strong>{selectedStory.title}</strong>"?
              <br />
              This action cannot be undone.
            </p>
            <div className="modal-actions">
              <button
                type="button"
                className="modal-btn cancel-modal-btn"
                onClick={cancelDelete}
              >
                Cancel
              </button>
              <button
                type="button"
                className="modal-btn delete-modal-btn"
                onClick={confirmDelete}
              >
                <Trash2 size={18} />
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
