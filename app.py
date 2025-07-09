from flask import Flask, request, send_file, render_template_string, after_this_request
from yt_dlp import YoutubeDL
import os
import shutil

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
  <title>YouDownload 🔻</title>
  <style>
    body {
      background: #0e0e0e;
      font-family: 'Segoe UI', sans-serif;
      color: #f1f1f1;
    }
    header {
      background: #e50914;
      padding: 20px;
      text-align: center;
      font-size: 28px;
    }
    .container {
      max-width: 700px;
      margin: 30px auto;
      background: #1a1a1a;
      padding: 30px;
      border-radius: 10px;
      border-top: 4px solid #e50914;
    }
    input[type="text"] {
      width: 100%;
      padding: 14px;
      margin-bottom: 20px;
      border-radius: 6px;
      border: 1px solid #444;
      background: #111;
      color: #fff;
    }
    .flex {
      display: flex;
      flex-wrap: wrap;
      gap: 15px;
      justify-content: space-between;
    }
    .section {
      flex: 1;
      min-width: 200px;
      background: #141414;
      padding: 15px;
      border-radius: 10px;
      text-align: center;
    }
    button, select {
      padding: 10px;
      margin-top: 10px;
      background: #e50914;
      border: none;
      color: white;
      border-radius: 6px;
      cursor: pointer;
      width: 100%;
    }
    button:hover {
      background: #ff1a1a;
    }
    select {
      background: #111;
      color: white;
    }
    .footer {
      margin-top: 40px;
      text-align: center;
      font-size: 13px;
      color: #888;
    }
  </style>
  <script>
    function setQuality(q) {
      document.getElementById("quality").value = q;
      document.getElementById("form").submit();
    }
    function setVideo() {
      let q = document.getElementById("video_quality").value;
      if (q) {
        setQuality(q);
      }
    }
  </script>
</head>
<body>

<header>YouDownload 🔻</header>

<div class="container">
  <form method="post" id="form">
    <input type="text" name="url" placeholder="Paste YouTube URL" required>
    <input type="hidden" name="quality" id="quality">

    <div class="flex">
      <div class="section">
        <h3>🎵 MP3 (320kbps)</h3>
        <button type="button" onclick="setQuality('mp3_320')">Download</button>
      </div>

      <div class="section">
        <h3>🎥 YouTube Video</h3>
        <select id="video_quality">
          <option value="">Select Quality</option>
          <option value="1080p">1080p</option>
          <option value="720p">720p</option>
          <option value="480p">480p</option>
        </select>
        <button type="button" onclick="setVideo()">Download</button>
      </div>

      <div class="section">
        <h3>🖼 Thumbnail</h3>
        <button type="button" onclick="setQuality('thumbnail')">Download</button>
      </div>
    </div>
  </form>
</div>

<div class="footer">
  ⚠️ This tool is for personal and educational use only.<br>
  Use responsibly. Built by <strong style="color: #e50914;">Abhi</strong>.
</div>

</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        quality = request.form['quality']
        os.makedirs("downloads", exist_ok=True)

        try:
            if quality == "mp3_320":
                ydl_opts = {
                    'format': 'bestaudio',
                    'outtmpl': 'downloads/%(title)s.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '0'
                    }],
                    'ffmpeg_location': r'C:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin'
                }

            elif quality == "1080p":
                ydl_opts = {
                    'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                    'outtmpl': 'downloads/%(title)s.%(ext)s',
                    'merge_output_format': 'mp4'
                }

            elif quality == "720p":
                ydl_opts = {
                    'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                    'outtmpl': 'downloads/%(title)s.%(ext)s',
                    'merge_output_format': 'mp4'
                }

            elif quality == "480p":
                ydl_opts = {
                    'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
                    'outtmpl': 'downloads/%(title)s.%(ext)s',
                    'merge_output_format': 'mp4'
                }

            elif quality == "thumbnail":
                with YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    thumb = info.get("thumbnail")
                    return f'''
                    <html><body>
                    <script>
                        window.location.href = "{thumb}";
                        setTimeout(() => {{
                            window.location.href = "/";
                        }}, 2000);
                    </script>
                    <p>Redirecting...</p>
                    </body></html>
                    '''

            else:
                return "❌ Unknown option selected."

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            if quality == "mp3_320":
                filename = os.path.splitext(filename)[0] + ".mp3"

            # Cleanup after sending file
            @after_this_request
            def remove_file(response):
                try:
                    os.remove(filename)
                except:
                    pass
                return response

            return send_file(filename, as_attachment=True)

        except Exception as e:
            return f"<h3 style='color:red;'>❌ Download failed or timed out: {str(e)}</h3>"

    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(debug=True)
