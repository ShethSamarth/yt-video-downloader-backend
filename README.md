# YouTube Video Downloader Backend

This project is a Flask-based web application that allows users to retrieve details about YouTube videos and download them in their desired resolution. It utilizes `yt-dlp` for video information extraction and downloading.

## Features

- **Get Video Details**: Retrieve video metadata, including title, description, channel, views, upload date, thumbnail, and available formats.
- **Download Videos**: Download YouTube videos in the desired resolution.
- **Serve Downloads**: Access downloaded videos through a dedicated endpoint.
- **Cleanup**: Remove all downloaded videos from the server.

## Requirements

- Python 3.7+
- `Flask`
- `Flask-CORS`
- `yt-dlp`

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ShethSamarth/yt-video-downloader-backend.git
   cd yt-video-downloader-backend
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**

   ```bash
   python app.py
   ```

   The application will run on `http://127.0.0.1:5000` by default.

## Endpoints

### 1. **Get Video Details**

- **URL**: `/get_video_details`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "url": "<YouTube video URL>"
  }
  ```
- **Response**:
  ```json
  {
    "title": "Video Title",
    "thumbnail": "URL to thumbnail",
    "description": "Video description",
    "channel": "Channel Name",
    "views": 123456,
    "upload_date": "YYYY-MM-DD",
    "formats": [
      {
        "format_id": "18",
        "resolution": "720p",
        "file_size": "5.23 MB",
        "ext": "mp4"
      }
    ]
  }
  ```

### 2. **Download Video**

- **URL**: `/download-video`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "url": "<YouTube video URL>",
    "resolution": "720"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Download successful",
    "file_name": "downloaded_video.mp4"
  }
  ```

### 3. **Get Video File**

- **URL**: `/get_video/<file_name>`
- **Method**: `GET`
- **Response**: Serves the requested video file for download.

### 4. **Cleanup Downloads**

- **URL**: `/cleanup`
- **Method**: `DELETE`
- **Response**:
  ```json
  {
    "message": "Cleanup successful."
  }
  ```

## Helper Functions

### `format_upload_date`

- Converts the upload date from `YYYYMMDD` format to `YYYY-MM-DD`.

### `sanitize_filename`

- Removes unsafe characters from file names and replaces spaces with underscores.

### `ensure_unique_filename`

- Ensures downloaded file names are unique by appending a counter if needed.

## Folder Structure

```
.
|-- app.py                # Main application file
|-- requirements.txt      # Python dependencies
|-- downloads/            # Directory to save downloaded videos
```

## Notes

- The app is configured to automatically merge audio and video streams into an MP4 file.
- A cleanup endpoint is provided to delete all downloaded files from the server.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

## Acknowledgements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for video downloading functionality.
- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [Flask-CORS](https://flask-cors.readthedocs.io/) for enabling CORS support.
