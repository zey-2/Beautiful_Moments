export type Photo = {
  id: number;
  story_id: number;
  file_path: string;
};

export type Story = {
  id: number;
  title: string;
  person: string;
  emotion: string;

  notes: string;
  generated_speech?: string;
  generated_voice_direction?: string;
  album_json?: string;
  audio_file_path?: string;
  used_in_presentation: boolean;
  created_at: string;
  photos: Photo[];
};

export type StoryCreate = {
  title: string;
  person: string;
  emotion: string;

  notes: string;
  files: File[];
};

export type AlbumLayout = {
  page_title: string;
  page_description: string;
  photos: {
    photo_id: string; // or number, depending on how we map it. The agent might return string indices.
    role: "main" | "side" | "background";
    caption: string;
  }[];
};
