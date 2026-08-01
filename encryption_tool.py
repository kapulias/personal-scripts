"""
A simple AES-CBC encryption/decryption TUI tool.
Only works with ascii text files.
"""

import asyncio
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, Label
from textual.containers import Grid, VerticalScroll


class AESManager:
    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, plaintext: str) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CBC)
        data = plaintext.encode("utf-8")
        padded_data = pad(data, AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        return cipher.iv + ciphertext

    def decrypt(self, ciphertext: bytes) -> str:
        iv = ciphertext[: AES.block_size]
        actual_ciphertext = ciphertext[AES.block_size :]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_plaintext = cipher.decrypt(actual_ciphertext)
        return unpad(padded_plaintext, AES.block_size).decode('utf-8')


class AESTuiApp(App):
    CSS = """
    Screen { align: center middle; }
    
    #main-container { 
        width: 95%; height: 95%; 
        border: solid $primary-darken-3; 
        padding: 1 2;
    }
    
    #file-display { 
        border: dashed $secondary; 
        height: auto; min-height: 3; 
        padding: 1; margin-bottom: 1;
        color: $text-muted;
    }
    
    #button-grid { 
        grid-size: 3; 
        grid-gutter: 1;
        margin-bottom: 1;
        height: auto;
    }
    
    Button { 
        min-width: 14; 
        width: 1fr; 
    } 
    
    #output-display { 
        border: double $success; 
        height: 10; min-height: 5;
        padding: 1; margin-top: 1;
        overflow-y: auto;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]

    def __init__(self):
        super().__init__()

        # ROT13 encoded key, see module 'this' (The Zen of Python)
        s = "xnchyvnf_cbxrzba"
        d = {}
        for c in (65, 97):
            for i in range(26):
                d[chr(i + c)] = chr((i + 13) % 26 + c)
        custom_key_str = "".join([d.get(c, c) for c in s])

        self.aes_manager = AESManager(custom_key_str.encode('utf-8'))
        self.selected_file = None

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="main-container"):
            yield Label("AES Encryptor & Decryptor")
            yield Static("No file selected.", id="file-display")

            with Grid(id="button-grid"):
                yield Button("Browse...", id="btn-browse", variant="primary")
                yield Button("Encrypt", id="btn-encrypt", variant="warning")
                yield Button("Decrypt", id="btn-decrypt", variant="success")

            yield Static("Ready.", id="output-display")
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        output_widget = self.query_one("#output-display", Static)

        if event.button.id == "btn-browse":
            try:
                from tkinter import Tk, filedialog

                root = Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                file_path = filedialog.askopenfilename(title="Select a File")
                root.destroy()

                if file_path:
                    self.selected_file = Path(file_path)
                    self.query_one("#file-display", Static).update(
                        f"Selected file: {self.selected_file}"
                    )
                    output_widget.update("File selected. Please click Encrypt or Decrypt.")
                else:
                    output_widget.update("File selection canceled.")
            except Exception as e:
                output_widget.update(
                    f"Error: Unable to open file dialog.\n{e}"
                )

        elif event.button.id in ("btn-encrypt", "btn-decrypt"):
            if not self.selected_file or not self.selected_file.exists():
                output_widget.update("Error: Please select a valid file first.")
                return

            is_encrypt = event.button.id == "btn-encrypt"
            action_verb = "Encrypting" if is_encrypt else "Decrypting"
            action_text = "Encryption" if is_encrypt else "Decryption"

            try:
                output_widget.update(f"{action_verb}...")
                await asyncio.sleep(0.1)

                if is_encrypt:
                    content = self.selected_file.read_text(encoding='utf-8')
                    result_bytes = self.aes_manager.encrypt(content)
                    out_path = self.selected_file.with_suffix('.enc.txt')
                    out_path.write_text(result_bytes.hex())
                    output_widget.update(
                        f"Successfully encrypted!\nCiphertext saved to: {out_path}"
                    )
                else:
                    raw_hex = self.selected_file.read_text(encoding='utf-8').strip()
                    decrypted = self.aes_manager.decrypt(bytes.fromhex(raw_hex))
                    out_path = self.selected_file.with_suffix('.dec.txt')
                    out_path.write_text(decrypted, encoding='utf-8')
                    output_widget.update(
                        f"Successfully decrypted!\nPlaintext saved to: {out_path}"
                    )

            except Exception as e:
                output_widget.update(f"{action_text} failed: {str(e)}")


if __name__ == "__main__":
    app = AESTuiApp()
    app.run()
