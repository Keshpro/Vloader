import customtkinter as ctk
import yt_dlp
import threading
import re
import requests
import io
from PIL import Image
from urllib.parse import urlparse

# Set the overall theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class VLoaderApp:
    def __init__(self):
        # --- Preloader (Splash Screen) ---
        self.splash = ctk.CTk()
        self.splash.title("VLoader Loading...")
        self.splash.geometry("400x300")
        self.splash.eval('tk::PlaceWindow . center')
        self.splash.overrideredirect(True)
        self.splash.configure(fg_color="#121212")

        accent_color = "#5a32fa"

        # --- App Name ---
        app_name = ctk.CTkLabel(self.splash, text="VLoader", font=("Helvetica", 36, "bold"), text_color=accent_color)
        app_name.pack(pady=(40, 10)) 

        # --- Names Frame ---
        names_frame = ctk.CTkFrame(self.splash, fg_color="transparent")
        names_frame.pack(pady=20) 

        fb_label = ctk.CTkLabel(names_frame, text="Facebook", font=("Helvetica", 12, "bold"), text_color=accent_color)
        fb_label.pack(side="left", padx=10) 

        insta_label = ctk.CTkLabel(names_frame, text="Instagram", font=("Helvetica", 12, "bold"), text_color=accent_color)
        insta_label.pack(side="left", padx=10)

        tiktok_label = ctk.CTkLabel(names_frame, text="TikTok", font=("Helvetica", 12, "bold"), text_color=accent_color)
        tiktok_label.pack(side="left", padx=10)

        yt_label = ctk.CTkLabel(names_frame, text="YouTube", font=("Helvetica", 12, "bold"), text_color=accent_color)
        yt_label.pack(side="left", padx=10)

        # --- Bottom Elements ---
        loading_text = ctk.CTkLabel(self.splash, text="Starting application...", font=("Helvetica", 12), text_color="#aaaaaa")
        loading_text.pack()

        copyright_mark = ctk.CTkLabel(self.splash, text="© KreativeLabs", font=("Helvetica", 10), text_color="#555555")
        copyright_mark.pack(side="bottom", pady=10)

        # Proceed to main app after 2 seconds
        self.splash.after(2000, self.start_main_app)
        self.splash.mainloop()

    def start_main_app(self):
        self.splash.destroy()
        self.show_main_window()

    def show_main_window(self):
        # --- Main Application Window ---
        self.app = ctk.CTk()
        self.app.title("VLoader - by KreativeLabs")
        self.app.geometry("700x480")
        self.app.eval('tk::PlaceWindow . center')
        self.app.configure(fg_color="#121212")

        # --- Grid Layout Configuration ---
        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_columnconfigure(1, weight=1)

        # --- Top Row: URL Input & Button ---
        self.url_input = ctk.CTkEntry(self.app, placeholder_text="Paste video link here...", height=40, corner_radius=8, fg_color="#1e1e1e", border_color="#333333")
        self.url_input.grid(row=0, column=0, columnspan=2, padx=(20, 10), pady=(20, 20), sticky="ew")

        # Bind the entry box to detect typing or pasting
        self.last_previewed_url = ""
        self.url_input.bind("<KeyRelease>", self.on_url_change)
        self.url_input.bind("<<Paste>>", self.on_url_change)

        self.download_btn = ctk.CTkButton(self.app, text="Download", command=self.start_download_thread, height=40, corner_radius=8, fg_color="#ff0645", hover_color="#1af030")
        self.download_btn.grid(row=0, column=2, padx=(0, 20), pady=(20, 20))

        # --- Left Column: Options ---
        self.options_frame = ctk.CTkFrame(self.app, fg_color="transparent")
        self.options_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.quality_label = ctk.CTkLabel(self.options_frame, text="Download Quality", text_color="#aaaaaa")
        self.quality_label.pack(anchor="w", pady=(0, 5))
        self.quality_dropdown = ctk.CTkComboBox(self.options_frame, values=["High (1080p / 720p)", "Medium (480p)", "Low (360p)"], height=35, corner_radius=8, fg_color="#1e1e1e", border_color="#333333")
        self.quality_dropdown.set("High (1080p / 720p)")
        self.quality_dropdown.pack(fill="x", pady=(0, 20))

        self.format_label = ctk.CTkLabel(self.options_frame, text="Format", text_color="#aaaaaa")
        self.format_label.pack(anchor="w", pady=(0, 5))
        self.format_seg_button = ctk.CTkSegmentedButton(self.options_frame, values=["Video (MP4)", "Audio (MP3)"], height=35, selected_color="#5a32fa", selected_hover_color="#4524c7")
        self.format_seg_button.set("Video (MP4)")
        self.format_seg_button.pack(fill="x", pady=(0, 20))

        # --- Right Column: Thumbnail Preview ---
        self.preview_frame = ctk.CTkFrame(self.app, fg_color="#1e1e1e", corner_radius=10, width=250, height=150)
        self.preview_frame.grid(row=1, column=1, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.preview_frame.grid_propagate(False)
        
        self.thumbnail_label = ctk.CTkLabel(self.preview_frame, text="[ Video Thumbnail Preview ]", text_color="#555555")
        self.thumbnail_label.place(relx=0.5, rely=0.5, anchor="center")

        # --- Bottom Row: Progress ---
        self.progress_frame = ctk.CTkFrame(self.app, fg_color="transparent")
        self.progress_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=(10, 10), sticky="ew")

        self.title_label = ctk.CTkLabel(self.progress_frame, text="Ready to download...", font=("Arial", 14, "bold"))
        self.title_label.pack(anchor="w", pady=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=10, corner_radius=5, progress_color="#5a32fa")
        self.progress_bar.set(0) 
        self.progress_bar.pack(fill="x", pady=(5, 5))

        self.status_frame = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        self.status_frame.pack(fill="x")
        self.status_label = ctk.CTkLabel(self.status_frame, text="", text_color="#aaaaaa", font=("Arial", 12))
        self.status_label.pack(side="left")
        self.speed_label = ctk.CTkLabel(self.status_frame, text="", text_color="#aaaaaa", font=("Arial", 12))
        self.speed_label.pack(side="right")

        # --- Legal / Warning Message ---
        legal_text = "LEGAL NOTICE: Only download content you have permission to use. Downloading copyrighted, adult, or illegal material is strictly prohibited."
        self.legal_label = ctk.CTkLabel(self.app, text=legal_text, text_color="#ff4d4d", font=("Arial", 10, "bold"))
        self.legal_label.grid(row=3, column=0, columnspan=3, pady=(0, 10))

        self.app.mainloop()

    # --- Auto Thumbnail Logic ---
    def on_url_change(self, event=None):
        # Add a tiny delay to ensure pasted text registers in the input box
        self.app.after(100, self.check_and_fetch_thumbnail)

    def check_and_fetch_thumbnail(self):
        url = self.url_input.get().strip()
        
        # Only run if it's a new link and starts with http
        if url.startswith("http") and url != self.last_previewed_url:
            self.last_previewed_url = url
            self.thumbnail_label.configure(text="[ Loading Preview... ⏳ ]", image="")
            
            # Start background thread to prevent freezing
            threading.Thread(target=self.fetch_thumbnail, args=(url,), daemon=True).start()
        elif not url:
            self.last_previewed_url = ""
            self.thumbnail_label.configure(text="[ Video Thumbnail Preview ]", image="")

    def fetch_thumbnail(self, url):
        ydl_opts = {'quiet': True, 'no_warnings': True}
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Look for the best thumbnail URL
                thumb_url = None
                if 'thumbnails' in info and len(info['thumbnails']) > 0:
                    thumb_url = info['thumbnails'][-1]['url']
                elif 'thumbnail' in info:
                    thumb_url = info['thumbnail']
                
                if thumb_url:
                    # Download the image
                    response = requests.get(thumb_url, timeout=5)
                    response.raise_for_status()
                    
                    # Convert it to a format CustomTkinter can display
                    img_data = response.content
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Store as a class variable to prevent it from disappearing (garbage collection)
                    self.current_thumbnail = ctk.CTkImage(light_image=img, dark_image=img, size=(240, 140))
                    
                    # Show it in the UI
                    self.app.after(0, lambda: self.thumbnail_label.configure(text="", image=self.current_thumbnail))
                else:
                    self.app.after(0, lambda: self.thumbnail_label.configure(text="[ No Thumbnail Found ]", image=""))
        except Exception as e:
            self.app.after(0, lambda: self.thumbnail_label.configure(text="[ Invalid Link / No Preview ]", image=""))

    # --- Backend Download Logic ---
    def update_progress_ui(self, percent, speed_text):
        self.progress_bar.set(percent)
        self.speed_label.configure(text=f"{speed_text}  |  {int(percent * 100)}%")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percent = downloaded / total
                speed = d.get('_speed_str', 'N/A')
                speed_clean = re.sub(r'\x1b\[[0-9;]*m', '', speed).strip()
                self.app.after(0, self.update_progress_ui, percent, speed_clean)
        elif d['status'] == 'finished':
            self.app.after(0, lambda: self.status_label.configure(text="Processing file... ⏳", text_color="yellow"))

    def start_download_thread(self):
        url = self.url_input.get().strip()
        if not url:
            self.status_label.configure(text="Please enter a valid link!", text_color="red")
            return
        
        # Domain Safety Whitelist Check
        allowed_domains = [
            "youtube.com", "youtu.be", 
            "facebook.com", "fb.watch", "fb.gg", 
            "instagram.com", 
            "tiktok.com"
        ]
        
        try:
            domain = urlparse(url).netloc.lower().replace("www.", "")
            is_allowed = any(domain.endswith(safe_site) for safe_site in allowed_domains)
        except Exception:
            is_allowed = False
            
        if not is_allowed:
            self.status_label.configure(text="Error: Only YouTube, Facebook, Insta, and TikTok are allowed!", text_color="red")
            return
        
        self.status_label.configure(text="Downloading... Please wait ⏳", text_color="#ff0127")
        self.title_label.configure(text="Fetching video info...")
        self.download_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.speed_label.configure(text="")
        
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def download_video(self, url):
        selected_format = self.format_seg_button.get()
        selected_quality = self.quality_dropdown.get()

        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self.progress_hook],
        }

        if selected_format == "Audio (MP3)":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            if "High" in selected_quality:
                ydl_opts['format'] = 'best[ext=mp4]/best' 
            elif "Medium" in selected_quality:
                ydl_opts['format'] = 'best[height<=480][ext=mp4]/best'
            else:
                ydl_opts['format'] = 'best[height<=360][ext=mp4]/best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_title = info_dict.get('title', 'Unknown Video')
                self.app.after(0, lambda: self.title_label.configure(text=video_title))
                
                ydl.download([url])
                
            self.app.after(0, lambda: self.status_label.configure(text="Download Successful!", text_color="green"))
            self.app.after(0, lambda: self.progress_bar.set(1.0))

        except yt_dlp.utils.DownloadError as e:
            if "ffmpeg is not installed" in str(e).lower():
                self.app.after(0, lambda: self.status_label.configure(text="Error: FFmpeg is missing! Put ffmpeg.exe in folder.", text_color="red"))
            else:
                self.app.after(0, lambda: self.status_label.configure(text="Download Failed! Check link.", text_color="red"))
        except Exception as e:
            self.app.after(0, lambda: self.status_label.configure(text="Download Failed! Something went wrong.", text_color="red"))
        finally:
            self.app.after(0, lambda: self.download_btn.configure(state="normal"))

if __name__ == "__main__":
    VLoaderApp()
