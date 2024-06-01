import sys
import base64
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
import cv2
from PIL import Image
import io
import asyncio
import aiohttp

class WhatabotHTTPClient:
    def __init__(self):
        self.api_key = "YOUR_API_KEY"
        self.phone = "YOUR_PHONE_NUMBER"
        self.url = "https://api.whatabot.io/Whatsapp/SendImage"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }

    async def send_image(self, image_base64):
        data = {
            "ApiKey": self.api_key,
            "Base64Image": image_base64,
            "Phone": self.phone
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=self.headers, json=data) as response:
                if response.status == 200:
                    print("Image sent successfully")
                    return True
                else:
                    print(f"Failed to send image. Status code: {response.status}")
                    return False

class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera App")
        self.setGeometry(100, 100, 640, 480)

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setGeometry(10, 10, 620, 400)

        self.capture_button = QPushButton("Capture", self)
        self.capture_button.setGeometry(270, 420, 100, 40)
        self.capture_button.clicked.connect(self.capture_image)

        self.camera = cv2.VideoCapture(0)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video)
        self.timer.start(50)

        self.whatabot_client = WhatabotHTTPClient()

    def update_video(self):
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_img))

    def capture_image(self):
        ret, frame = self.camera.read()
        if ret:
            # Convert to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Resize image and convert to base64
            with io.BytesIO() as output:
                pil_image.resize((400, 300)).save(output, format="JPEG", quality=90)
                image_bytes = output.getvalue()
                image_base64 = base64.b64encode(image_bytes).decode()

            # Send image
            success = asyncio.run(self.whatabot_client.send_image(image_base64))
            if success:
                self.show_alert("Success", "Image sent successfully!")
            else:
                self.show_alert("Error", "Failed to send image. Check your API key or your remaining messages")
                

    def show_alert(self, title, message):
        alert = QMessageBox()
        alert.setWindowTitle(title)
        alert.setText(message)
        alert.setIcon(QMessageBox.Information)
        alert.addButton(QMessageBox.Ok)
        alert.exec_()

    def closeEvent(self, event):
        self.camera.release()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
