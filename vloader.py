import customtkinter as ctk
import yt_dlp
import threading

# App eke theme eka Dark karamu
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class VLoaderApp:
    def __init__(self):
        # --- Preloader (Splash Screen) ---
        self.splash = ctk.CTk()
        self.splash.title("VLoader Loading...")
        self.splash.geometry("400x250")
        self.splash.eval('tk::PlaceWindow . center')
        self.splash.overrideredirect(True)

        app_name = ctk.CTkLabel(self.splash, text="VLoader", font=("Helvetica", 36, "bold"), text_color="#FF0000")
        app_name.pack(pady=(70, 10))

        loading_text = ctk.CTkLabel(self.splash, text="Starting application...", font=("Helvetica", 12))
        loading_text.pack()

        copyright_mark = ctk.CTkLabel(self.splash, text="© KreativeLabs", font=("Helvetica", 10), text_color="gray")
        copyright_mark.pack(side="bottom", pady=10)

        self.splash.after(2000, self.start_main_app)
        self.splash.mainloop()

    def start_main_app(self):
        self.splash.destroy()
        self.show_main_window()

    def show_main_window(self):
        # --- Main Application Window ---
        self.app = ctk.CTk()
        self.app.title("VLoader - by KreativeLabs")
        self.app.geometry("500x350")
        self.app.eval('tk::PlaceWindow . center')

        title_label = ctk.CTkLabel(self.app, text="VLoader Downloader", font=("Helvetica", 24, "bold"))
        title_label.pack(pady=(20, 20))

        self.url_input = ctk.CTkEntry(self.app, placeholder_text="Paste YouTube Link Here...", width=400, height=40)
        self.url_input.pack(pady=10)

        options_frame = ctk.CTkFrame(self.app, fg_color="transparent")
        options_frame.pack(pady=10)

        self.format_var = ctk.StringVar(value="Video (MP4)")
        self.format_dropdown = ctk.CTkOptionMenu(options_frame, values=["Video (MP4)", "Audio (MP3)"], variable=self.format_var)
        self.format_dropdown.grid(row=0, column=0, padx=10)

        self.quality_var = ctk.StringVar(value="High (1080p / 720p)")
        self.quality_dropdown = ctk.CTkOptionMenu(options_frame, values=["High (1080p / 720p)", "Medium (480p)", "Low (360p)"], variable=self.quality_var)
        self.quality_dropdown.grid(row=0, column=1, padx=10)

        self.status_label = ctk.CTkLabel(self.app, text="", font=("Helvetica", 12))
        self.status_label.pack(pady=5)

        self.download_btn = ctk.CTkButton(self.app, text="Download Now", command=self.start_download_thread, fg_color="#FF0000", hover_color="#CC0000")
        self.download_btn.pack(pady=10)
        
        footer = ctk.CTkLabel(self.app, text="© KreativeLabs", font=("Helvetica", 10), text_color="gray")
        footer.pack(side="bottom", pady=10)

        self.app.mainloop()

    def start_download_thread(self):
        url = self.url_input.get()
        if not url:
            self.status_label.configure(text="Please enter a valid link!", text_color="red")
            return
        
        self.status_label.configure(text="Downloading... Please wait ⏳", text_color="yellow")
        self.download_btn.configure(state="disabled")
        
        threading.Thread(target=self.download_video, args=(url,)).start()

    def download_video(self, url):
        selected_format = self.format_var.get()
        selected_quality = self.quality_var.get()

        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }

        # FFmpeg error eka magaharinna Fallback formats dunna (Merging avoid karanawa)
        if selected_format == "Audio (MP3)":
            ydl_opts['format'] = 'bestaudio/best'
            # Note: MP3 convert karanna nam aniwaren FFmpeg ona. 
            # E nisa bestaudio widihata eka bawanawa (godak welawata .m4a hari .webm hari widihata ei FFmpeg nathnam).
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            if "High" in selected_quality:
                # Merging error eka nathuwa ganna best format eka gannawa (Up to 720p with audio usually)
                ydl_opts['format'] = 'best[ext=mp4]/best' 
            elif "Medium" in selected_quality:
                ydl_opts['format'] = 'best[height<=480][ext=mp4]/best'
            else:
                ydl_opts['format'] = 'best[height<=360][ext=mp4]/best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.configure(text="Download Successful! 🎉 (Saved in app folder)", text_color="green")
        except yt_dlp.utils.DownloadError as e:
            if "ffmpeg is not installed" in str(e).lower():
                self.status_label.configure(text="Error: FFmpeg is missing! Put ffmpeg.exe in folder.", text_color="red")
            else:
                self.status_label.configure(text="Download Failed! Check link or internet.", text_color="red")
            print(e)
        except Exception as e:
            self.status_label.configure(text="Download Failed! Something went wrong.", text_color="red")
            print(e)
        finally:
            self.download_btn.configure(state="normal")

if __name__ == "__main__":
    VLoaderApp()