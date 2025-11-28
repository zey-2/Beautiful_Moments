# Beautiful Moments Storytelling App

The Beautiful Moments Storytelling App is a dual-mode application designed to transform special moments into dynamic, emotionally resonant experiences. It leverages Google's Gemini AI to generate speech passages based on user-provided metadata and photos, with a premium black and gold interface.

## Features

- **Edit Mode**: Create, edit, and delete stories with AI-generated speech content
  - Select existing stories to edit all fields including generated speech
  - Upload and manage photos (up to 4 per story)
  - Delete stories with confirmation dialog
  - Premium black and gold themed interface
- **Present Mode**: Distraction-free, full-screen teleprompter for speeches
  - Focus entirely on speech text (photos hidden)
  - Automatic "presented" status tracking
  - Reset all story statuses with one click
  - Premium styling with gold accents
- **AI Integration**: Gemini 2.5 Flash for generating valedictorian-style speech passages
- **Local Storage**: SQLite database and local file storage for easy development

## Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **Google Gemini API Key**

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
    - Add your Gemini API Key:
      ```
      GEMINI_API_KEY=your_actual_api_key_here
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
cd frontend; npm run dev
```

The frontend will typically start at `http://localhost:5173` (or `5174` if the port is busy). Check the terminal output for the exact URL.

## How to Use

### Edit Mode (Story Management)

1.  Open the app in your browser (e.g., `http://localhost:5173`).
2.  Navigate to the **Edit** tab.

#### Creating a New Story
3.  **Fill in the form**:
    - **Title**: Name of the story/memory
    - **Person**: Who the story is about
    - **Emotion**: The emotional tone (e.g., "nostalgic", "joyful", "bittersweet")
    - **Notes**: Context and details for the AI to generate the speech
    - **Photos**: Upload up to 4 photos (optional)
4.  Click **Create Story**.
5.  **AI Generation**: Gemini will generate a ~100-word valedictorian-style passage based on your inputs.
6.  The new story appears in the sidebar.

#### Editing an Existing Story
1.  Click on any story in the sidebar to load it into the form.
2.  Edit any field including:
    - Title, person, emotion, notes
    - **Generated speech** (you can manually refine the AI output)
    - Add or remove photos
3.  Click **Save Changes** to update.
4.  Click **Cancel** or the **+** button to create a new story.

#### Deleting a Story
1.  While editing a story, click the **trash icon** in the header.
2.  Confirm the deletion in the dialog.
3.  The story and all associated photos are permanently deleted.

### Present Mode (Live Speech)

1.  Navigate to the **Present** tab.
2.  You will see a grid of all created stories.
3.  **Select a Story**: Click on a card to open the full-screen teleprompter view.
    - Displays the speech text in a premium black and gold interface
    - Photos are hidden to minimize distractions during presentation
4.  **Mark as Presented**: Once a story is opened, it is automatically marked as "Presented" and will appear dimmed in the grid view.
5.  **Reset All Stories**: Click the **Reset All** button to clear all "Presented" statuses.
6.  **Close**: Click the **X** button to return to the grid.

## API Endpoints

The backend provides the following REST API endpoints:

- `POST /stories/` - Create a new story with photos
- `GET /stories/` - Get all stories
- `GET /stories/{id}` - Get a specific story
- `PUT /stories/{id}` - Update a story
- `DELETE /stories/{id}` - Delete a story and its photos
- `POST /stories/{id}/mark_used` - Mark a story as presented
- `POST /stories/reset` - Reset all stories' presented status
- `POST /stories/{id}/photos` - Add photos to an existing story
- `DELETE /stories/photos/{photo_id}` - Delete a specific photo

## Project Structure

```
V_speech_core/
├── backend/                      # FastAPI Backend
│   ├── routers/
│   │   └── stories.py            # Story API endpoints
│   ├── agents.py                 # Gemini AI integration
│   ├── models.py                 # SQLAlchemy & Pydantic models
│   ├── database.py               # Database configuration
│   ├── main.py                   # FastAPI app entry point
│   ├── migrate_remove_topic.py   # Database migration script
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
│   │   │   └── PresentMode.css  # Present mode styling
│   │   ├── api.ts               # API client functions
│   │   ├── types.ts             # TypeScript type definitions
│   │   ├── App.tsx              # Main app component
│   │   ├── App.css              # App-level styling
│   │   ├── index.css            # Global styles & theme
│   │   └── main.tsx             # React entry point
│   ├── package.json             # Node dependencies
│   └── vite.config.ts           # Vite configuration
├── media/                        # Uploaded photos storage
├── stories.db                    # SQLite database
├── design_doc.md                 # Original design document
├── UPDATE_SUMMARY.md             # Feature update summary
├── DELETE_STORY_IMPLEMENTATION.md # Delete feature docs
└── README.md                     # This file
```

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation
- **Google GenAI SDK** - Gemini API integration
- **SQLite** - Local database
- **Uvicorn** - ASGI server

### Frontend
- **React 19** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **Framer Motion** - Animation library

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
- `generated_speech` - AI-generated speech text
- `album_json` - Photo layout data (JSON)
- `used_in_presentation` - Boolean flag
- `created_at` - Timestamp
- `updated_at` - Timestamp

### Photos Table
- `id` - Primary key
- `story_id` - Foreign key to stories
- `file_path` - Path to uploaded image

## Development Notes

- The "topic" field was removed in a previous update (see `UPDATE_SUMMARY.md`)
- Photos are currently hidden in Present Mode to focus on the teleprompter
- Album layout generation is still functional but not displayed
- Database migrations are handled via custom Python scripts
- All photos are stored in the `media/` directory

## Future Enhancements

Potential features for future development:
- Photo editing and reordering in Edit Mode
- Story reordering/prioritization
- Export stories to PDF or text
- Import/export functionality for backup
- Multi-user support with authentication
- Cloud deployment (Docker support)
- Custom themes and color schemes
