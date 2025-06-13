import tkinter as tk
from tkinter import filedialog, messagebox
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google_auth_oauthlib.flow
from dotenv import load_dotenv

load_dotenv()
SERVICE = 'youtube'
SERVICE_VERSION = 'v3'
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = os.getenv('GOOGLE_CLIENT_SECRETS_FILE')

# ADD Token Caching
# USE from_client_config instead of from_client_secrets_file for public deployment. Then provide a json format with client ID
def get_authenticated_service():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        SCOPES
    )
    credentials = flow.run_local_server(port=0)
    return build(SERVICE, SERVICE_VERSION, credentials=credentials)


def upload_video(file_path, title, description, privacy_status, tags=None):
    try:
        youtube = get_authenticated_service()
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": "20",  # Gaming
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
        chunks_used = 0

        while response is None:
            status, response = request.next_chunk()
            chunks_used += 1

            if status:
                print(f"Using Chunk: {chunks_used} -> Uploading... {int(status.progress() * 100)}%")
        print(f"Upload 100% Complete! Used: {chunks_used} chunks.")
        messagebox.showinfo("Success", f"Upload 100% Complete! Used: {chunks_used} chunks. Video ID: {response['id']}")

        return {
            "video_id": response["id"],
            "title": title,
            "player": description,
            "social_link": "",
            "tags": tags or [],
            "url": "/" + os.path.basename(file_path)
        }

    except Exception as e:
        messagebox.showerror("Upload Failed", str(e))
        return None


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

        result = upload_video(path, title_val, desc_val, privacy_val, tags=tags_val)
        if result:
            result_str = (
                "{\n"
                f'      video_id: "{result["video_id"]}",\n'
                f'      title: "{result["title"]}",\n'
                f'      player: "{result["player"]}",\n'
                f'      social_link: "{result["social_link"]}",\n'
                f'      tags: {result["tags"]},\n'
                f'      url: "{result["url"]}"\n'
                "},"
            )

            # Display in popup
            top = tk.Toplevel()
            top.title("Video Object JSON")
            text = tk.Text(top, wrap="word", width=80, height=10)
            text.insert(tk.END, result_str)
            text.config(state="normal")
            text.pack(padx=10, pady=10)
            tk.Button(top, text="Copy to Clipboard", command=lambda: root.clipboard_append(result_str)).pack(pady=(0,10))

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
    tk.Label(root, text="Tags (comma-separated)").grid(row=2, column=0, sticky="ne", pady=2)
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
