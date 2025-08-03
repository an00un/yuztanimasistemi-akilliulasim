import flet as ft
import cv2
import threading
import face_recognition
import firebase_admin
from firebase_admin import credentials, storage, db
import os
from datetime import datetime, timedelta
import base64
import time

cred_storage = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred_storage, {
    'storageBucket': 'keyllogger-440b8.appspot.com'
}, name='storage')

cred_db = credentials.Certificate("serviceAccount_db.json")
firebase_admin.initialize_app(cred_db, {
    'databaseURL': 'https://yuztanimasistemi-kolayulasim-default-rtdb.firebaseio.com/'
}, name='db')

storage_app = firebase_admin.get_app(name='storage')
db_app = firebase_admin.get_app(name='db')

default_screen = "seyahat"
current_screen = default_screen
plaka_global = ""

def load_known_faces():
    print("Yüz verileri Firebase'den yükleniyor...")
    bucket = storage.bucket(app=storage_app)
    known_encodings = []
    known_ids = []

    blobs = bucket.list_blobs(prefix="yuzgoruntuleri")
    os.makedirs("temp_faces", exist_ok=True)

    for blob in blobs:
        if blob.name.endswith(('.jpg', '.jpeg', '.png')):
            tc_id = os.path.basename(blob.name).split('.')[0]
            local_path = f"temp_faces/{tc_id}.jpg"
            blob.download_to_filename(local_path)

            image = face_recognition.load_image_file(local_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                known_ids.append(tc_id)
    return known_encodings, known_ids

class CameraThread(threading.Thread):
    def __init__(self, image_element, name_text, balance_text, tc_text, status_text):
        super().__init__()
        self.image_element = image_element
        self.name_text = name_text
        self.balance_text = balance_text
        self.tc_text = tc_text
        self.status_text = status_text
        self.running = True
        self.known_encodings, self.known_ids = load_known_faces()

    def run(self):
        cap = cv2.VideoCapture(0)
        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for encoding in face_encodings:
                matches = face_recognition.compare_faces(self.known_encodings, encoding)
                if True in matches:
                    matched_idx = matches.index(True)
                    tc = self.known_ids[matched_idx]
                    self.tc_text.value = f"T.C.: {tc}"
                    now = datetime.now()

                    user_ref = db.reference(f"users/dogrulanmamis/{tc}", app=db_app)
                    user_data = user_ref.get()
                    if user_data:
                        name = user_data.get("adsoyad", "Bilinmiyor")
                        bakiye = float(user_data.get("bakiye", 0))
                        self.name_text.value = f"Ad Soyad: {name}"
                        self.balance_text.value = f"Bakiye: {bakiye:.2f} TL"

                        last_time_str = user_data.get("son_kullanim")
                        last_time = datetime.fromisoformat(last_time_str) if last_time_str else None

                        if last_time and now - last_time < timedelta(seconds=30):
                            self.status_text.value = "Lütfen ilerleyiniz"

                        elif (last_time and timedelta(seconds=30) <= now - last_time <= timedelta(minutes=2)) and user_data.get("plaka") != plaka_global:
                            self.status_text.value = "Aktarma - Ücret alınmadı"
                            user_ref.update({"son_kullanim": now.isoformat(), "plaka": plaka_global})
                            self._update_all()
                            time.sleep(2)
                            self._clear_all()

                        elif bakiye < 5:
                            global current_screen
                            current_screen = "bakiye_yetersiz"
                            self.status_text.value = "Yetersiz Bakiye"

                        else:
                            user_ref.update({
                                "bakiye": bakiye - 5,
                                "son_kullanim": now.isoformat(),
                                "plaka": plaka_global
                            })
                            self.status_text.value = "Ücret alındı"
                    break

            frame = cv2.resize(frame, (640, 480))
            _, buffer = cv2.imencode(".png", frame)
            self.image_element.src_base64 = base64.b64encode(buffer).decode("utf-8")
            self._update_all()

        cap.release()

    def stop(self):
        self.running = False

    def _update_all(self):
        self.image_element.update()
        self.name_text.update()
        self.balance_text.update()
        self.tc_text.update()
        self.status_text.update()

    def _clear_all(self):
        self.name_text.value = ""
        self.balance_text.value = ""
        self.tc_text.value = ""
        self.status_text.value = ""
        self._update_all()

def main(page: ft.Page):
    global plaka_global
    page.title = "Yüz Tanıma - Akıllı Ulaşım"
    page.window_width = 640
    page.window_height = 480

    plaka_input = ft.TextField(label="Araç Plakası", width=300, color="white")
    start_button = ft.ElevatedButton(text="Sistemi Başlat")

    def start_system(e):
        nonlocal plaka_input, start_button
        global plaka_global
        plaka_global = plaka_input.value.strip().upper()
        if not plaka_global:
            return
        start_button.disabled = True
        plaka_input.disabled = True
        page.update()
        setup_system()

    start_button.on_click = start_system

    page.add(
        ft.Column([
            ft.Text("Lütfen araç plakasını girin", size=20, color="white"),
            plaka_input,
            start_button
        ], width=1200, height=480, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    def setup_system():
        page.controls.clear()

        camera_feed = ft.Image(width=320, height=240)
        name_text = ft.Text(value="", size=20, color="white")
        balance_text = ft.Text(value="", size=20, color="white")
        tc_text = ft.Text(value="", size=20, color="white")
        status_text = ft.Text(value="", size=20, color="yellow")

        layout = ft.Stack([])
        cam_thread = None

        def update_ui():
            layout.controls.clear()
            if current_screen == "seyahat":
                layout.controls.append(ft.Text("Araç seyir halinde...", size=30, color="white"))
            elif current_screen == "kamera":
                layout.controls.append(
                    ft.Column([
                        camera_feed,
                        name_text,
                        balance_text,
                        tc_text,
                        status_text
                    ], alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            elif current_screen == "bakiye_yetersiz":
                layout.controls.append(ft.Text("Yetersiz Bakiye!", size=40, color="red"))
            page.update()

        def on_key(e: ft.KeyboardEvent):
            nonlocal cam_thread
            global current_screen

            if e.key == "F1":
                current_screen = "kamera"
                update_ui()
                if cam_thread is None or not cam_thread.is_alive():
                    cam_thread = CameraThread(camera_feed, name_text, balance_text, tc_text, status_text)
                    cam_thread.start()

            elif e.key == "F2":
                current_screen = "bakiye_yetersiz"
                update_ui()
                if cam_thread:
                    cam_thread.stop()

            elif e.key == "F3":
                current_screen = "seyahat"
                update_ui()
                if cam_thread:
                    cam_thread.stop()

        page.on_keyboard_event = on_key
        page.add(layout)
        update_ui()

ft.app(target=main)
