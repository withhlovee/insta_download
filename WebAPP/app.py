# app.py
from flask import Flask, render_template, request, send_file
import instaloader
import os
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'downloads'

# Create downloads directory if not exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def download_reel(reel_url, username, password):
    loader = instaloader.Instaloader(
        dirname_pattern=app.config['UPLOAD_FOLDER'],
        save_metadata=False,
        download_videos=True,
        download_video_thumbnails=False
    )
    
    try:
        loader.login(username, password)
    except Exception as e:
        return None, f"Login failed: {str(e)}"

    if '/reel/' not in reel_url:
        return None, "Invalid Instagram Reel URL"
    
    shortcode = reel_url.split("/reel/")[-1].split("/")[0]
    
    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target=str(uuid.uuid4()))
        
        # Find the downloaded file
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            if file.endswith('.mp4'):
                return os.path.join(app.config['UPLOAD_FOLDER'], file), None
        
        return None, "Video file not found"
    except Exception as e:
        return None, str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        username = request.form['username']
        password = request.form['password']
        
        file_path, error = download_reel(url, username, password)
        
        if error:
            return render_template('index.html', error=error)
        
        # Clean up other files (keep only the MP4)
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            if not f.endswith('.mp4'):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name='instagram_reel.mp4'
        )
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)