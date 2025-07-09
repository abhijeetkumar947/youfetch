from flask import Flask, request, send_file, render_template_string
from yt_dlp import YoutubeDL
import os
import shutil

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
  <title>YouDownload</title>
  <style>
    body {
      background-color: #000;
      color: #fff;
      font-family: Arial, sans-serif;
      text-align: center;
      padding: 50px;
    }
    .container {
      background: #111;
      border: 2px solid #e50914;
      padding: 30px;
      border-radius: 10px;
      display: inline-block;
    }
    input[type=text] {
      width: 90%%;
      padding: 10px;
      margin: 10px 0;
      border-radius: 6px;
      border: 1px solid #e50914;
      background: #222;
      color: #fff;
    }
    button {
      padding: 10px 15px;
      margin: 5px;
      border: none;
      border-radius: 6px;
      background-color: #e50914;
      color: white;
      cursor: pointer;
    }
    .footer {
      margin-top: 40px;
      font-size: 0.9em;
      color: #aaa;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>YouDownload</h1>
    <form method="post">
      <input type="text" name="url" placeholder="Paste YouTube URL here" required><br>
      <button name="action" value="mp3">🎵 Download MP3 (320kbps)</button>
      <button name="action" value="1080p">📺 Download 1080p</button>
      <button name="action" value="720p">📺 Download 720p</button>
      <button name="action" value="480p">📺 Download 480p</button>
      <button name="action" value="thumbnail">🖼️ Download Thumbnail</button>
    </form>
  </div>
  <div class="footer">© 2025 YouDownload | Created by Abhi</div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        action = request.form['action']

        os.makedirs("downloads", exist_ok=True)

        # Use browser-like headers
        common_opts = {
            'quiet': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            },
            'outtmpl': 'downloads/%(title)s.%(ext)s'
        }

        try:
            if action == "mp3":
                ydl_opts = common_opts.copy()
                ydl_opts.update({
                    'format': 'bestaudio',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '0'
                    }]
                })

            elif action in ["1080p", "720p", "480p"]:
                height = {"1080p": "1080", "720p": "720", "480p": "480"}[action]
                ydl_opts = common_opts.copy()
                ydl_opts.update({
                    'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]',
                    'merge_output_format': 'mp4'
                })

            elif action == "thumbnail":
                with YoutubeDL(common_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    thumbnail_url = info.get('thumbnail')
                    if thumbnail_url:
                        import requests
                        r = requests.get(thumbnail_url, stream=True)
                        thumb_file = 'downloads/thumbnail.jpg'
                        with open(thumb_file, 'wb') as f:
                            shutil.copyfileobj(r.raw, f)
                        return send_file(thumb_file, as_attachment=True)
                    else:
                        return "❌ Thumbnail not found."

            else:
                return "❌ Invalid action selected."

            # For video/audio downloads
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            # Rename file for mp3
            if action == "mp3":
                filename = os.path.splitext(filename)[0] + ".mp3"

            return send_file(filename, as_attachment=True)

        except Exception as e:
            return render_template_string(HTML + f"<p style='color:red;'>❌ Download failed or timed out:<br>{str(e)}</p>")

    return render_template_string(HTML)

if __name__ == '__main__':
    print("✅ Flask app is running...")
    app.run(debug=True)
