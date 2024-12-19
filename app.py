import os
import re
from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Directory to save downloaded videos
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


def format_upload_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return "N/A"


def sanitize_filename(filename):
    """Sanitize filenames by removing spaces and unsafe characters."""
    filename = re.sub(r'[\\/*?:"<>|]', '', filename)  # Remove unsafe characters
    return filename.replace(' ', '_')  # Replace spaces with underscores


def ensure_unique_filename(filepath):
    """Ensure the filename is unique by appending a number if the file already exists."""
    base, ext = os.path.splitext(filepath)
    counter = 1
    while os.path.exists(filepath):
        filepath = f"{base}_{counter}{ext}"
        counter += 1
    return filepath


@app.route('/get_video_details', methods=['POST'])
def get_video_details():
    try:
        # Get the YouTube URL from the request
        data = request.json
        url = data.get('url')

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        # Configure YoutubeDL options
        options = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,  # Avoid downloading the video
        }

        # Fetch video details
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)

        # Format file size (helper function)
        def format_filesize(size):
            if not size:
                return "Unknown"
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.2f} {unit}"
                size /= 1024
            return f"{size:.2f} TB"

        # Construct the response
        response = {
            "title": info.get('title', 'N/A'),
            "thumbnail": info.get('thumbnail', 'N/A'),
            "description": info.get('description', 'N/A'),
            "channel": info.get('channel', 'N/A'),
            "views": info.get('view_count', 0),
            "upload_date": format_upload_date(info.get('upload_date')),
            "formats": [
                {
                    "format_id": f.get('format_id', 'N/A'),
                    "resolution": f"{f['height']}p" if f.get('height') else "audio only",
                    "file_size": format_filesize(f.get('filesize')),
                    "ext": f.get('ext', 'N/A'),
                }
                for f in info.get('formats', [])
            ],
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch video details: {str(e)}"}), 500


@app.route('/download-video', methods=['POST'])
def download_video():
    try:
        # Get data from the request
        data = request.json
        url = data.get('url')
        resolution = data.get('resolution')

        # Validate URL
        if not url or not re.match(r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$', url):
            return jsonify({"error": "Invalid YouTube URL"}), 400

        if not resolution:
            return jsonify({"error": "No Resolution provided"}), 400

        # Configure yt-dlp options
        options = {
            'format': f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',  # Merge audio and video into MP4
            'quiet': True,
            'no_warnings': True,
        }

        # Download the video
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # Sanitize file name
        sanitized_name = sanitize_filename(os.path.basename(file_path))
        sanitized_path = os.path.join(DOWNLOAD_FOLDER, sanitized_name)

        # Ensure the file path is unique (avoid overwriting)
        unique_path = ensure_unique_filename(sanitized_path)

        # Rename the file if necessary
        if unique_path != sanitized_path:
            os.rename(file_path, unique_path)
        else:
            os.rename(file_path, sanitized_path)

        # Return success response
        return jsonify({
            "message": "Download successful",
            "file_name": os.path.basename(unique_path),
        })

    except Exception as e:
        return jsonify({"error": f"Failed to download video: {str(e)}"}), 500


@app.route('/get_video/<file_name>', methods=['GET'])
def get_video(file_name):
    try:
        # Secure the file path
        file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
        file_path = os.path.abspath(file_path)

        # Ensure file is within the DOWNLOAD_FOLDER
        if not file_path.startswith(os.path.abspath(DOWNLOAD_FOLDER)):
            return jsonify({"error": "Invalid file path"}), 403

        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        # Serve the file
        return send_file(file_path, as_attachment=True, download_name=file_name)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/cleanup', methods=['DELETE'])
def cleanup():
    for file in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            return jsonify({"error": f"Failed to delete {file}: {str(e)}"}), 500

    return jsonify({"message": "Cleanup successful."})


if __name__ == '__main__':
    app.run(debug=True)
