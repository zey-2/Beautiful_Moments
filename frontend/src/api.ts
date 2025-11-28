import axios from "axios";
import type { Story, StoryCreate } from "./types";

const API_URL = "http://localhost:8000/api";

export const api = axios.create({
  baseURL: API_URL,
});

export const getStories = async (): Promise<Story[]> => {
  const response = await api.get("/stories");
  return response.data;
};

export const createStory = async (story: StoryCreate): Promise<Story> => {
  const formData = new FormData();
  formData.append("title", story.title);
  formData.append("person", story.person);
  formData.append("emotion", story.emotion);
  formData.append("notes", story.notes);

  story.files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await api.post("/stories/", formData);
  return response.data;
};

export const markStoryUsed = async (id: number): Promise<void> => {
  await api.post(`/stories/${id}/mark_used`);
};

export const resetStories = async (): Promise<void> => {
  await api.post("/stories/reset");
};

export const updateStory = async (
  id: number,
  story: Partial<Story>
): Promise<Story> => {
  const response = await api.put(`/stories/${id}`, story);
  return response.data;
};

export const deleteStory = async (id: number): Promise<void> => {
  await api.delete(`/stories/${id}`);
};

export const addPhotosToStory = async (
  storyId: number,
  files: File[]
): Promise<void> => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });
  await api.post(`/stories/${storyId}/photos`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const deletePhoto = async (photoId: number): Promise<void> => {
  await api.delete(`/stories/photos/${photoId}`);
};

export const regenerateTranscript = async (storyId: number): Promise<{ generated_speech: string; generated_voice_direction: string }> => {
  const response = await api.post(`/stories/${storyId}/regenerate_transcript`);
  return {
    generated_speech: response.data.generated_speech,
    generated_voice_direction: response.data.generated_voice_direction
  };
};

export const regenerateAudio = async (storyId: number, speechText?: string): Promise<string> => {
  const formData = new FormData();
  if (speechText) {
    formData.append("speech_text", speechText);
  }
  const response = await api.post(`/stories/${storyId}/regenerate_audio`, formData);
  return response.data.audio_file_path;
};

export const verifyPassword = async (password: string): Promise<{ success: boolean; message?: string }> => {
  const response = await api.post("/verify-password", { password });
  return response.data;
};


