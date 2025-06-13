# AI Short Video Creator API Documentation

## Table of Contents
- [Overview](#overview)
- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Image Generation API](#image-generation-api)
  - [Endpoint](#endpoint)
  - [Request](#request)
  - [Response](#response)
  - [How It Works](#how-it-works)
  - [Parameters](#parameters)
- [Video Creation API](#video-creation-api)
  - [Endpoint](#endpoint-1)
  - [Request](#request-1)
  - [Response](#response-1)
  - [How It Works](#how-it-works-1)
  - [Parameters](#parameters-1)
- [Complete Workflow Example](#complete-workflow-example)
- [Troubleshooting](#troubleshooting)
- [Additional Notes](#additional-notes)

---

## Overview

This API provides two main functionalities:

- **Image Generation** – Creates images from text scripts using Hugging Face's Stable Diffusion XL.
- **Video Creation** – Combines generated images into a video with transitions, captions, and audio.

---

## Setup

### Prerequisites

- Python 3.8+
- Hugging Face API token
- FFmpeg (required for video processing)

### Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Hugging Face token:
   ```
   HUGGINGFACE_TOKEN=your_token_here
   ```

5. Run the server:
   ```bash
   python app.py
   ```

---

## Image Generation API

### Endpoint

**POST** `/api/image/`

### Request

```json
{
  "script": "A beautiful landscape with mountains and a sunset. The sky is painted with vibrant orange and purple hues. A small cabin sits by a serene lake, with tall pine trees surrounding it."
}
```

### Response

```json
{
  "data": [
    "output/image_1_uuid.png",
    "output/image_2_uuid.png",
    "output/image_3_uuid.png"
  ]
}
```

### How It Works

- The script is split into sentences (using periods as separators).
- Each sentence is processed by the Stable Diffusion model.
- Generated images are saved to the `output` directory.
- The API returns paths to all generated images.

### Parameters

| Parameter | Type   | Description                                                             |
|-----------|--------|-------------------------------------------------------------------------|
| script    | string | The input text script to generate images from. Complete sentences only. |

---

## Video Creation API

### Endpoint

**POST** `/api/video/`

### Request

```json
{
  "image_paths": ["output/image_1.png", "output/image_2.png", "output/image_3.png"],
  "fps": 24,
  "duration_per_image": 3,
  "add_transitions": true,
  "add_captions": true,
  "captions": ["First scene description", "Second scene description", "Third scene description"],
  "audio_path": "assets/background_music.mp3"
}
```

### Response

```json
{
  "data": "output/video_uuid.mp4"
}
```

### How It Works

- Takes a list of image paths (or all images in output folder if not provided).
- Creates a video clip for each image with the specified duration.
- Adds transitions between clips if `add_transitions` is true.
- Adds captions to each image if `add_captions` is true.
- Adds background audio if `audio_path` is provided.
- Combines everything into a single video file.
- Returns the path to the generated video.

### Parameters

| Parameter           | Type    | Required | Default         | Description                                       |
|---------------------|---------|----------|-----------------|---------------------------------------------------|
| image_paths         | array   | No       | All output PNGs | List of paths to images for the video             |
| fps                 | number  | No       | 24              | Frames per second for the video                   |
| duration_per_image  | number  | No       | 2               | Seconds to display each image                     |
| add_transitions     | boolean | No       | false           | Whether to add fade transitions between images    |
| add_captions        | boolean | No       | false           | Whether to add text captions to images            |
| captions            | array   | No       | null            | List of caption texts (one per image)             |
| audio_path          | string  | No       | null            | Path to background audio file                     |

---

## Complete Workflow Example

1. **Generate Images from Script**
2. **Create Video with Generated Images**

---

## Troubleshooting

### Image Generation

- **Error 401**: Invalid Hugging Face token. Check your `.env` file.
- **No images generated**: Script may be too short or lacks proper sentence structure.
- **Slow generation**: Stable Diffusion XL is computationally intensive.

### Video Creation

- `ModuleNotFoundError: No module named 'moviepy.editor'`:
  ```bash
  pip install moviepy
  ```
- **Missing ffmpeg**:
  - Install FFmpeg and ensure it's in your system PATH.

- **No video created**:
  - Ensure there are valid images in the output directory.

---

## Additional Notes

- Image generation quality depends on the descriptiveness of your script.
- For best results, use detailed, visual descriptions in each sentence.
- The API automatically skips sentences shorter than 10 characters.