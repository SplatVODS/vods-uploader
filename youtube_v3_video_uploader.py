import tkinter as tk
from tkinter import filedialog, messagebox
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google_auth_oauthlib.flow
from os import getenv
from dotenv import load_dotenv
import os


load_dotenv()
SERVICE = 'youtube'
SERVICE_VERSION = 'v3'
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = getenv('GOOGLE_CLIENT_SECRETS_FILE')


def get_authenticated_service():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        SCOPES
    )
    credentials = flow.run_local_server(port=800)
    return build(SERVICE, SERVICE_VERSION, credentials=credentials)


def upload_video(file_path, title, description, privacy_status, tags=None):
    # ADD LOGIC TO APPEND TAGS INTO A LIST GOES HERE
    # IT WILL BE A COMMA SEPARATED INPUT, MAKE SURE TO TAKE OUT EXTRA WHITE SPACE
    try:
        youtube = get_authenticated_service()
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": "20",  # gaming, https://mixedanalytics.com/blog/list-of-youtube-video-category-ids/
            },
            "status": {
                "privacyStatus": privacy_status
            }
        }

        media = MediaFileUpload(filename=file_path, resumable=True)
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploading... {int(status.progress() * 100)}%")
        print(f"Uploading... 100%")

        messagebox.showinfo("Success", f"Upload Complete! Video ID: {response['id']}")
    except Exception as e:
        messagebox.showerror("Upload Failed", str(e))


# GUI Setup
def open_gui():
    def browse_file():
        selected = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
        if selected:
            file_path.set(selected)
            file_path_display.config(text=os.path.basename(selected))

    def start_upload():
        path = file_path.get()
        title_val = title.get()
        desc_val = description.get("1.0", tk.END).strip()
        raw_tags = tags.get("1.0", tk.END).strip()
        tags_val = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]
        privacy_val = privacy_status.get()

        if not path or not title_val:
            messagebox.showwarning("Missing Info", "Please select a file and enter a title.")
            return

        upload_video(path, title_val, desc_val, privacy_val, tags=tags_val)

    root = tk.Tk()
    root.title("YouTube Video Uploader")
    root.configure(padx=10, pady=10)

    def on_closing():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing) 

    # Title
    tk.Label(root, text="Title").grid(row=0, column=0, sticky="e", pady=2)
    title = tk.Entry(root, width=50)
    title.grid(row=0, column=1, pady=2)

    # Description
    tk.Label(root, text="Description").grid(row=1, column=0, sticky="ne", pady=2)
    description = tk.Text(root, width=50, height=4)
    description.grid(row=1, column=1, pady=2)

    # Tags
    tk.Label(root, text="Tags").grid(row=2, column=0, sticky="ne", pady=2)
    tags = tk.Text(root, width=50, height=2)
    tags.grid(row=2, column=1, pady=2)

    # Privacy
    tk.Label(root, text="Privacy").grid(row=3, column=0, sticky="e", pady=2)
    privacy_status = tk.StringVar(value="public")
    tk.OptionMenu(root, privacy_status, "public", "private", "unlisted").grid(
        row=3,
        column=1,
        sticky="w",
        pady=2
    )

    # Video File
    tk.Label(root, text="Video File").grid(row=4, column=0, sticky="e", pady=2)
    file_path = tk.StringVar()
    file_path_display = tk.Label(root, text="No file selected", anchor="w", width=40, relief="sunken")
    file_path_display.grid(row=4, column=1, sticky="w", pady=2)
    tk.Button(root, text="Browse", command=browse_file).grid(
        row=4,
        column=1,
        sticky="e",
        pady=2
    )

    # Upload Button
    tk.Button(root, text="Upload", command=start_upload, bg="green", fg="white", height=2, width=20).grid(
        row=5,
        column=0,
        columnspan=2,
        pady=10
    )

    root.mainloop()


if __name__ == "__main__":
    open_gui()
