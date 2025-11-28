# Beautiful Moments Storytelling App

The Beautiful Moments Storytelling App is a dual-mode application designed to transform special moments into dynamic, emotionally resonant experiences. It leverages Google's Gemini AI with advanced workflow orchestration to generate speech passages, voice directions, and audio narration based on user-provided metadata and photos, featuring a premium black and gold interface with password-protected editing.

## Features

### Edit Mode (Password Protected)
- **Authentication**: Secure password protection for edit mode access (configured via `.env`)
- **Story Management**: Create, edit, and delete stories with AI-generated content
  - Select existing stories to edit all fields including generated speech
  - Upload and manage photos (up to 4 per story)
  - Delete stories with confirmation dialog
  - Premium black and gold themed interface
- **AI-Powered Content Generation**:
  - **Speech Generation**: Gemini 2.5 Flash creates ~100-word valedictorian-style passages
  - **Voice Direction**: AI generates emotional voice performance cues (e.g., "Voice: Warm, enthusiastic, filled with genuine delight")
  - **Audio Synthesis**: Gemini 2.5 Flash TTS generates natural-sounding audio with voice direction
  - **Album Layout**: AI designs photo layouts with roles (main, side, background) and captions
  - **Google Search Integration**: AI can search the web for current information when generating content
- **Regeneration Controls**:
  - Regenerate speech transcript and voice direction
  - Regenerate audio from updated speech text
  - Manual editing of all AI-generated content

### Present Mode (Public Access)
- **Distraction-Free Teleprompter**: Full-screen view optimized for live presentations
  - Focus entirely on speech text (photos hidden)
  - Audio playback with generated narration
  - Automatic "presented" status tracking
  - Reset all story statuses with one click
  - Premium styling with gold accents
- **Default Landing Page**: Present mode is the default view for public access

### AI Architecture
- **Workflow Agents**: Sequential agent orchestration for coherent multi-step processes
  - `LlmAgent`: Configurable AI agents with system instructions and prompt templates
  - `SequentialAgent`: Chains multiple agents with shared state
- **Structured Output**: Pydantic models ensure consistent, validated AI responses
- **Logging**: Comprehensive debug logging for LLM requests and responses

## Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **Google Gemini API Key** (with access to Gemini 2.5 Flash and TTS models)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository_url>
cd V_speech_core
```

### 2. Backend Setup

The backend is built with FastAPI.

1.  **Create and activate a virtual environment**:

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

2.  **Install dependencies**:

    ```bash
    pip install -r backend/requirements.txt
    ```

3.  **Configure Environment Variables**:
    - Rename `backend/.env.example` to `backend/.env`.
    - Add your credentials:
      ```
      GEMINI_API_KEY=your_actual_api_key_here
      EDIT_PASSWORD=your_password_here
      ```

### 3. Frontend Setup

The frontend is built with React, TypeScript, and Vite.

1.  **Navigate to the frontend directory**:

    ```bash
    cd frontend
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

## Running the Application

You need to run both the backend and frontend servers.

### 1. Start the Backend

From the root directory (make sure your venv is activated):

```bash
# Windows
venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000

# Mac/Linux
python -m uvicorn backend.main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`.

### 2. Start the Frontend

From the `frontend` directory:

```bash
cd frontend
npm run dev
```

The frontend will typically start at `http://localhost:5173` (or `5174` if the port is busy). Check the terminal output for the exact URL.

## How to Use

### Accessing the Application

1.  Open the app in your browser (e.g., `http://localhost:5173`).
2.  **Default View**: You'll land on **Present Mode** (public access).
3.  **Edit Mode**: Click the "Edit" tab and enter the password configured in `.env`.

### Edit Mode (Story Management)

#### Authentication
1.  Navigate to the **Edit** tab.
2.  Enter the password from your `.env` file (`EDIT_PASSWORD`).
3.  Click **Enter** to access edit mode.
4.  Use the **Logout** button to exit edit mode.

#### Creating a New Story
1.  **Fill in the form**:
    - **Title**: Name of the story/memory
    - **Person**: Who the story is about
    - **Emotion**: The emotional tone (e.g., "nostalgic", "joyful", "bittersweet")
    - **Notes**: Context and details for the AI to generate the speech
    - **Photos**: Upload up to 4 photos (optional)
2.  Click **Create Story**.
3.  **AI Generation Process**:
    - Gemini generates a ~100-word speech passage with emotional voice direction
    - TTS engine creates audio narration with the specified voice characteristics
    - Album layout AI designs photo arrangements with captions
4.  The new story appears in the sidebar with all generated content.

#### Editing an Existing Story
1.  Click on any story in the sidebar to load it into the form.
2.  Edit any field including:
    - Title, person, emotion, notes
    - **Generated speech** (manually refine the AI output)
    - **Voice direction** (adjust emotional performance cues)
    - Add or remove photos
3.  **Regeneration Options**:
    - Click **Regenerate Speech** to create new transcript and voice direction
    - Click **Regenerate Audio** to create new audio from current speech text
4.  Click **Save Changes** to update.
5.  Click **Cancel** or the **+** button to create a new story.

#### Viewing AI-Generated Content
- **Speech Text**: Displayed in the main text area (editable)
- **Voice Direction**: Shown above the speech text (e.g., "(Voice: Warm and reflective)")
- **Album Layout**: JSON structure displayed below the form
- **Audio Player**: Playback controls for generated narration

#### Deleting a Story
1.  While editing a story, click the **trash icon** in the header.
2.  Confirm the deletion in the dialog.
3.  The story and all associated photos and audio files are permanently deleted.

### Present Mode (Live Presentation)

1.  Navigate to the **Present** tab (or visit the root URL).
2.  You will see a grid of all created stories.
3.  **Select a Story**: Click on a card to open the full-screen teleprompter view.
    - Displays the speech text in a premium black and gold interface
    - Audio player for generated narration
    - Photos are hidden to minimize distractions during presentation
4.  **Mark as Presented**: Once a story is opened, it is automatically marked as "Presented" and will appear dimmed in the grid view.
5.  **Reset All Stories**: Click the **Reset All** button to clear all "Presented" statuses.
6.  **Close**: Click the **X** button to return to the grid.

## API Endpoints

The backend provides the following REST API endpoints:

### Story Management
- `POST /api/stories/` - Create a new story with photos (triggers AI generation)
- `GET /api/stories/` - Get all stories
- `GET /api/stories/{id}` - Get a specific story
- `PUT /api/stories/{id}` - Update a story
- `DELETE /api/stories/{id}` - Delete a story and its photos/audio

### Presentation
- `POST /api/stories/{id}/mark_used` - Mark a story as presented
- `POST /api/stories/reset` - Reset all stories' presented status

### Photo Management
- `POST /api/stories/{id}/photos` - Add photos to an existing story
- `DELETE /api/stories/photos/{photo_id}` - Delete a specific photo

### AI Regeneration
- `POST /api/stories/{id}/regenerate_transcript` - Regenerate speech and voice direction
- `POST /api/stories/{id}/regenerate_audio` - Regenerate audio from speech text

### Authentication
- `POST /api/verify-password` - Verify edit mode password

### Static Files
- `GET /media/{filename}` - Serve uploaded photos and audio files

## Project Structure

```
V_speech_core/
├── backend/                      # FastAPI Backend
│   ├── routers/
│   │   └── stories.py            # Story API endpoints
│   ├── agents.py                 # Gemini AI integration (speech, audio, album)
│   ├── workflow.py               # Workflow agent framework (LlmAgent, SequentialAgent)
│   ├── models.py                 # SQLAlchemy & Pydantic models
│   ├── database.py               # Database configuration
│   ├── main.py                   # FastAPI app entry point
│   ├── migrate_*.py              # Database migration scripts
│   ├── verify_*.py               # Verification/testing scripts
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment template
│   └── .env                      # Environment variables (not in git)
├── frontend/                     # React + TypeScript Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── StoryCard.tsx    # Story card component
│   │   │   ├── StoryCard.css    # Card styling
│   │   │   └── ErrorBoundary.tsx # Error handling
│   │   ├── pages/
│   │   │   ├── EditMode.tsx     # Story creation/editing page
│   │   │   ├── EditMode.css     # Edit mode styling
│   │   │   ├── PresentMode.tsx  # Presentation page
│   │   │   ├── PresentMode.css  # Present mode styling
│   │   │   ├── Login.tsx        # Authentication page
│   │   │   └── Login.css        # Login styling
│   │   ├── api.ts               # API client functions
│   │   ├── types.ts             # TypeScript type definitions
│   │   ├── App.tsx              # Main app component with routing
│   │   ├── App.css              # App-level styling
│   │   ├── index.css            # Global styles & theme
│   │   └── main.tsx             # React entry point
│   ├── package.json             # Node dependencies
│   └── vite.config.ts           # Vite configuration
├── media/                        # Uploaded photos and audio files
├── stories.db                    # SQLite database
├── list_models.py                # Utility to list available Gemini models
└── README.md                     # This file
```

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation and structured outputs
- **Google GenAI SDK (v1.16.0+)** - Gemini API integration
  - Gemini 2.5 Flash Lite - Text generation
  - Gemini 2.5 Flash Preview TTS - Audio synthesis
  - Google Search Tool - Web search integration
- **SQLite** - Local database
- **Uvicorn** - ASGI server
- **Pillow** - Image processing
- **python-dotenv** - Environment variable management

### Frontend
- **React 19** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **Framer Motion** - Animation library

### AI Workflow Architecture
- **Custom Workflow Framework** (`workflow.py`):
  - `Agent` - Abstract base class for all agents
  - `LlmAgent` - Configurable LLM agent with state management
  - `SequentialAgent` - Orchestrates multi-step agent pipelines
- **State Management**: Shared dictionary passed between agents
- **Structured Outputs**: Pydantic models for validation
- **Logging**: Debug-level logging for all LLM interactions

## Design Theme

The app features a premium **black and gold** color scheme:

- **Background**: Pure black (#000000) with dark gray accents (#111111, #1a1a1a)
- **Primary**: Gold (#d4af37) and light gold (#f4d03f)
- **Text**: White (#ffffff) and gray (#a0a0a0)
- **Accents**: Gold borders, gradients, and hover effects
- **Animations**: Smooth transitions and micro-interactions throughout

## Database Schema

### Stories Table
- `id` - Primary key
- `title` - Story title
- `person` - Person the story is about
- `emotion` - Emotional tone
- `notes` - Context for AI generation
- `generated_speech` - AI-generated speech text (editable)
- `generated_voice_direction` - AI-generated voice performance cues
- `album_json` - Photo layout data (JSON)
- `audio_file_path` - Path to generated audio file
- `used_in_presentation` - Boolean flag
- `created_at` - Timestamp
- `updated_at` - Timestamp

### Photos Table
- `id` - Primary key
- `story_id` - Foreign key to stories
- `file_path` - Path to uploaded image

## AI Generation Details

### Speech Generation
- **Model**: Gemini 2.5 Flash Lite
- **System Instruction**: Valedictorian speech style, ~100 words
- **Output**: Structured JSON with `emotion` and `transcript` fields
- **Tools**: Google Search (for current information)
- **Features**: 
  - Emotional voice direction in parentheses
  - Performance cues (e.g., "(pause)", "(slight chuckle)")
  - Thematically unified around user's story

### Audio Generation
- **Model**: Gemini 2.5 Flash Preview TTS
- **Voice**: Despina (prebuilt voice)
- **Input**: Speech text + voice direction
- **Output**: WAV file (24kHz, mono, 16-bit PCM)
- **Storage**: Saved to `media/` directory

### Album Layout Generation
- **Model**: Gemini 2.5 Flash Lite
- **Input**: Story metadata + uploaded images
- **Output**: JSON with page title, description, and photo entries
- **Validation**: Ensures photo IDs match provided images
- **Photo Roles**: main, side, background
- **Captions**: Max 20 words per photo

## Development Notes

### Logging
- Backend uses Python's `logging` module at DEBUG level
- LLM requests and responses are logged for debugging
- Format: `%(asctime)s - %(levelname)s - %(name)s - %(message)s`

### Environment Variables
Required in `backend/.env`:
- `GEMINI_API_KEY` - Your Google Gemini API key
- `EDIT_PASSWORD` - Password for edit mode access

## Troubleshooting

### API Key Issues
- Ensure `GEMINI_API_KEY` is set in `backend/.env`
- Check that the key has access to required models
- Use `list_models.py` to verify available models

### Audio Generation Issues
- Requires Gemini 2.5 Flash Preview TTS access
- Check model availability in your region
- Audio files saved to `media/` directory

### Authentication Issues
- Ensure `EDIT_PASSWORD` is set in `backend/.env`
- Clear browser localStorage if login persists incorrectly
- Check backend logs for password verification errors


