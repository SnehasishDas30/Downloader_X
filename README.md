# Downloader X 🚀

**Downloader X** is a powerful media downloader that supports YouTube, Pinterest, and multiple other platforms. It uses a **Flask backend** along with **yt-dlp + FFmpeg** for downloading, merging, and previewing videos and audio. Real-time progress, optional cloud upload, and admin panel features are included.  

---

## Features ✨

- 🎬 **Video & Audio Download**: Download media from YouTube, Pinterest, and other supported platforms.  
- 🔗 **Preview Before Download**: Preview video or audio before downloading.  
- ⚡ **High-Quality Merge**: Automatically merges `bestvideo + bestaudio` into MP4.  
- 🔒 **Cookies Support**: Works with YouTube restricted or private videos.  
- ☁️ **Optional Cloud Upload**: Push downloaded files to cloud storage.  
- 📊 **Real-Time Progress**: Frontend shows download progress dynamically.  
- 🛠️ **Admin Panel**: Built-in admin dashboard for management.  

---

## Tech Stack 🛠️

- **Backend**: Python 3 + Flask  
- **Video Processing**: yt-dlp, static FFmpeg  
- **Frontend**: Vanilla JavaScript, HTML, CSS  
- **Deployment**: GitHub → Render  
- **Database**: SQLite (optional)  

---

## Installation & Setup ⚙️

1. **Clone the repository:**

```bash
git clone https://github.com/<your-username>/Downloader_X.git
cd Downloader_X




#Install dependencies:

pip install -r requirements.txt


Set up required files and folders:

downloads/ → for storing downloaded media

cookies.txt → optional, for YouTube login

Run the Flask server:

python app.py


Server will be available at http://127.0.0.1:5000

#Usage 📌

Open the web interface in your browser.

Paste the video URL into the input box.

Click Preview to check the media.

Click Download to start downloading.

Monitor the progress bar for real-time updates.

