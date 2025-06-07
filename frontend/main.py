import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk  
import requests
import os
import time
import vlc
from PIL import Image, ImageTk
import threading  


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  


API_URL_UPLOAD = "http://127.0.0.1:8000/upload/"
HIGHLIGHT_PATH = "D:/FOOTECH/backend/Goal_Clips/extracted_clip.mp4"


def upload_file():
    """Upload a video file to the backend."""
    file_path = filedialog.askopenfilename(
        title="Select Football Match Video",
        filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv")]
    )
    if not file_path:
        return

    if not os.path.isfile(file_path):
        messagebox.showerror("Error", "Invalid file selected.")
        return

    status_label.configure(text="Uploading match video...", text_color="#4CAF50")
    root.update()

   
    threading.Thread(target=upload_file_thread, args=(file_path,), daemon=True).start()

def upload_file_thread(file_path):
    try:
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(API_URL_UPLOAD, files=files)
        if response.status_code == 200:
           
            root.after(0, lambda: status_label.configure(text="Video processing initiated...", text_color="#2196F3"))
            video_path = response.json().get("video_path")
            
            root.after(0, lambda: process_highlights(video_path))
        else:
            root.after(0, lambda: status_label.configure(text="Processing error", text_color="#F44336"))
            root.after(0, lambda: messagebox.showerror("Error", f"Failed to process video: {response.text}"))
    except Exception as e:
        root.after(0, lambda: status_label.configure(text="Upload failed", text_color="#F44336"))
        root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))

def process_highlights(video_path):
    """Update progress and enable play once processing is complete."""
    def progress_loop(i=1):
        if i <= 100:
            progress_bar.set(i / 100.0)
            status_label.configure(text=f"Analyzing commentary... {i}%", text_color="#2196F3")
            root.after(50, lambda: progress_loop(i+2))
        else:
            status_label.configure(text="Highlights generated successfully!", text_color="#4CAF50")
            play_button.configure(state=ctk.NORMAL)
    progress_loop()

def play_video():
    """Play the highlight video with VLC embedded in a CustomTkinter Toplevel window."""
    if not os.path.exists(HIGHLIGHT_PATH):
        messagebox.showerror("Error", "Highlight video not found!")
        return

    
    window = ctk.CTkToplevel(root)
    window.title("Highlight Playback")
    window.geometry("900x500")
    
   
    video_panel = tk.Frame(window, bg="black")
    video_panel.pack(fill=tk.BOTH, expand=True)
    
   
    instance = vlc.Instance()
    player = instance.media_player_new()
    media = instance.media_new(HIGHLIGHT_PATH)
    player.set_media(media)
    if os.name == "nt":
        player.set_hwnd(video_panel.winfo_id())
    else:
        player.set_xwindow(video_panel.winfo_id())
    
    controls = ctk.CTkFrame(window, fg_color="#1E1E1E", corner_radius=15)
    controls.pack(fill=tk.X, padx=20, pady=10)
    

    time_label_v = ctk.CTkLabel(controls, text="0:00 / 0:00", font=("Inter", 14), text_color="white")
    time_label_v.pack(side=tk.LEFT, padx=10)
    

    video_slider = ctk.CTkSlider(controls, from_=0, to=100, width=500, command=lambda val: set_video_position(val))
    video_slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    def update_slider():
        if player.get_length() > 0:
            total_time = player.get_length() / 1000
            current_time = player.get_time() / 1000
            time_label_v.configure(text=f"{int(current_time//60)}:{int(current_time%60):02d} / {int(total_time//60)}:{int(total_time%60):02d}")
            video_slider.configure(to=total_time)
            video_slider.set(current_time)
        window.after(500, update_slider)

    def set_video_position(val):
        player.set_time(int(float(val) * 1000))

    def play():
        player.play()

    def pause():
        player.pause()

    def stop():
        player.stop()

    def key_handler(event):
        if event.keysym == "Right":
            player.set_time(player.get_time() + 5000)
        elif event.keysym == "Left":
            player.set_time(player.get_time() - 5000)
    
    window.bind("<KeyPress>", key_handler)

   
    btn_frame = ctk.CTkFrame(controls, fg_color="#1E1E1E", corner_radius=10)
    btn_frame.pack(side=tk.RIGHT, padx=10)
    
    play_btn = ctk.CTkButton(btn_frame, text="Play", command=play, fg_color="#00B894", text_color="white", font=("Inter", 14), corner_radius=8, width=80)
    play_btn.grid(row=0, column=0, padx=5, pady=5)
    pause_btn = ctk.CTkButton(btn_frame, text="Pause", command=pause, fg_color="#00B894", text_color="white", font=("Inter", 14), corner_radius=8, width=80)
    pause_btn.grid(row=0, column=1, padx=5, pady=5)
    stop_btn = ctk.CTkButton(btn_frame, text="Stop", command=stop, fg_color="#00B894", text_color="white", font=("Inter", 14), corner_radius=8, width=80)
    stop_btn.grid(row=0, column=2, padx=5, pady=5)
    
    player.play()
    update_slider()


root = ctk.CTk()
root.title("FOOTECH: Highlight Generator")
root.geometry("900x750")
root.configure(fg_color="#121212")


container = ctk.CTkFrame(root, fg_color="#222222", corner_radius=25)
container.place(relx=0.5, rely=0.5, relwidth=0.9, relheight=0.9, anchor=tk.CENTER)


title = ctk.CTkLabel(
    container,
    text="FOOTECH\nHighlight Generator",
    font=("Inter", 40, "bold"),
    text_color="white",
    fg_color="transparent"
)
title.pack(pady=(50, 30))


upload_button = ctk.CTkButton(
    container,
    text="Upload Match Video",
    command=upload_file,
    fg_color="#0077CC",
    text_color="white",
    font=("Inter", 22, "bold"),
    corner_radius=12,
    hover_color="#005fa3"
)
upload_button.pack(fill=tk.X, padx=150, pady=15)


status_label = ctk.CTkLabel(
    container,
    text="Upload football match video for highlight generation",
    font=("Inter", 18),
    text_color="#E0E0E0",
    fg_color="transparent"
)
status_label.pack(pady=10)


progress_bar = ctk.CTkProgressBar(container, width=700, height=15)
progress_bar.set(0)
progress_bar.pack(pady=20)


play_button = ctk.CTkButton(
    container,
    text="Play Highlights",
    command=play_video,
    state=ctk.DISABLED,
    fg_color="#00B894",
    text_color="white",
    font=("Inter", 22, "bold"),
    corner_radius=12,
    hover_color="#008f72"
)
play_button.pack(fill=tk.X, padx=150, pady=15)

play_button._text_label.configure(fg="white")

root.mainloop()
