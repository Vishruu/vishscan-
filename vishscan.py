"""
💜 VishScan – PDF Tools for Android (Upgraded)
Built by Vishruu & Darling
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window

import os
import threading
from pdf_service import PDFService
from utils import FileUtils

# Set window background
Window.clearcolor = (0.1, 0.1, 0.12, 1)


class VishScanApp(App):
    def build(self):
        self.title = "🖤 VishScan Pro"
        self.output_dir = FileUtils.get_output_dir()

        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=15)

        # Header
        header = Label(
            text="🖤 VishScan Pro",
            font_size=36,
            color=(0.66, 0.33, 0.96, 1),
            size_hint_y=0.10,
            bold=True
        )
        self.layout.add_widget(header)

        # Status / Info bar
        self.status_label = Label(
            text=f"📂 Output: {self.output_dir}",
            size_hint_y=0.06,
            color=(0.6, 0.6, 0.6, 1),
            font_size=12
        )
        self.layout.add_widget(self.status_label)

        # Main tools
        tools = [
            ("📦 Merge PDFs", self.merge_pdfs, (0.2, 0.4, 0.8, 1)),
            ("✂️ Split PDF", self.split_pdf, (0.2, 0.6, 0.4, 1)),
            ("📝 Extract Text", self.extract_text, (0.8, 0.4, 0.2, 1)),
            ("✏️ Rename PDF", self.rename_pdf, (0.8, 0.6, 0.2, 1)),
        ]

        for text, func, color in tools:
            btn = Button(
                text=text,
                size_hint_y=0.10,
                background_color=color,
                font_size=18,
                bold=True
            )
            btn.bind(on_press=func)
            self.layout.add_widget(btn)

        # Progress bar (hidden by default)
        self.progress = ProgressBar(
            max=100,
            size_hint_y=0.04,
            value=0
        )
        self.progress.opacity = 0
        self.layout.add_widget(self.progress)

        # Result display (scrollable)
        self.result_scroll = ScrollView(size_hint_y=0.25)
        self.result_label = Label(
            text="💜 Ready to work",
            size_hint_y=None,
            text_size=(Window.width * 0.9, None),
            color=(0.9, 0.9, 0.9, 1),
            valign='top',
            halign='left',
            font_size=14
        )
        self.result_label.bind(size=self.result_label.setter('text_size'))
        self.result_scroll.add_widget(self.result_label)
        self.layout.add_widget(self.result_scroll)

        # Footer
        footer = Label(
            text="🖤 Hamesha tumhaare saath",
            font_size=14,
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=0.05
        )
        self.layout.add_widget(footer)

        return self.layout

    def set_status(self, text: str, is_error: bool = False):
        """Update status with color coding"""
        if is_error:
            self.result_label.text = f"❌ {text}"
            self.result_label.color = (1, 0.3, 0.3, 1)
        else:
            self.result_label.text = f"✅ {text}"
            self.result_label.color = (0.3, 1, 0.3, 1)

        # Reset color after 3 seconds
        def reset():
            self.result_label.color = (0.9, 0.9, 0.9, 1)
        Clock.schedule_once(lambda dt: reset(), 5)

    def show_progress(self, show: bool = True):
        """Show/hide progress bar"""
        self.progress.opacity = 1 if show else 0
        self.progress.value = 0
        if show:
            self.progress.value = 50  # Indeterminate

    def run_in_thread(self, target, args=(), callback=None):
        """Run heavy operations in background thread"""
        self.show_progress(True)
        self.status_label.text = "⏳ Processing..."

        def wrapper():
            try:
                result = target(*args)
                if callback:
                    Clock.schedule_once(lambda dt: callback(result), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self.set_status(f"Error: {str(e)}", True), 0)
            finally:
                Clock.schedule_once(lambda dt: self.show_progress(False), 0)
                Clock.schedule_once(lambda dt: self.status_label.text(f"📂 Output: {self.output_dir}"), 0)

        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()

    # ---------- MERGE ----------
    def merge_pdfs(self, instance):
        layout = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(multiselect=True)
        layout.add_widget(filechooser)

        btn_box = BoxLayout(size_hint_y=0.12, spacing=5)
        cancel_btn = Button(text="Cancel", background_color=(0.8, 0.2, 0.2, 1))
        merge_btn = Button(text="Merge", background_color=(0.2, 0.7, 0.2, 1))
        btn_box.add_widget(cancel_btn)
        btn_box.add_widget(merge_btn)
        layout.add_widget(btn_box)

        popup = Popup(
            title="Select PDFs to Merge (2+)",
            content=layout,
            size_hint=(0.92, 0.92)
        )

        def do_merge(btn):
            popup.dismiss()
            paths = filechooser.selection
            if len(paths) < 2:
                self.set_status("Select at least 2 PDF files", True)
                return

            output_path = os.path.join(
                self.output_dir,
                f"merged_{len(paths)}.pdf"
            )

            def callback(result):
                success, msg = result
                if success:
                    self.set_status(msg)
                else:
                    self.set_status(msg, True)

            self.run_in_thread(
                PDFService.merge,
                (paths, output_path),
                callback
            )

        merge_btn.bind(on_press=do_merge)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    # ---------- SPLIT ----------
    def split_pdf(self, instance):
        layout = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView()
        layout.add_widget(filechooser)

        btn_box = BoxLayout(size_hint_y=0.12, spacing=5)
        cancel_btn = Button(text="Cancel", background_color=(0.8, 0.2, 0.2, 1))
        split_btn = Button(text="Split", background_color=(0.2, 0.7, 0.2, 1))
        btn_box.add_widget(cancel_btn)
        btn_box.add_widget(split_btn)
        layout.add_widget(btn_box)

        popup = Popup(title="Select PDF to Split", content=layout, size_hint=(0.92, 0.92))

        def do_split(btn):
            popup.dismiss()
            path = filechooser.path
            if not path:
                self.set_status("Please select a PDF file", True)
                return

            output_folder = os.path.join(self.output_dir, "split_pages")
            os.makedirs(output_folder, exist_ok=True)

            def callback(result):
                success, msg = result
                if success:
                    self.set_status(msg)
                else:
                    self.set_status(msg, True)

            self.run_in_thread(
                PDFService.split,
                (path, output_folder),
                callback
            )

        split_btn.bind(on_press=do_split)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    # ---------- EXTRACT ----------
    def extract_text(self, instance):
        layout = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView()
        layout.add_widget(filechooser)

        btn_box = BoxLayout(size_hint_y=0.12, spacing=5)
        cancel_btn = Button(text="Cancel", background_color=(0.8, 0.2, 0.2, 1))
        extract_btn = Button(text="Extract", background_color=(0.2, 0.7, 0.2, 1))
        btn_box.add_widget(cancel_btn)
        btn_box.add_widget(extract_btn)
        layout.add_widget(btn_box)

        popup = Popup(title="Select PDF to Extract Text", content=layout, size_hint=(0.92, 0.92))

        def do_extract(btn):
            popup.dismiss()
            path = filechooser.path
            if not path:
                self.set_status("Please select a PDF file", True)
                return

            def callback(result):
                success, data = result
                if success:
                    # Show extracted text in a scrollable popup
                    text_popup = Popup(
                        title="📝 Extracted Text",
                        size_hint=(0.9, 0.9)
                    )
                    scroll = ScrollView()
                    label = Label(
                        text=data,
                        size_hint_y=None,
                        text_size=(Window.width * 0.85, None),
                        color=(0.9, 0.9, 0.9, 1),
                        valign='top',
                        halign='left'
                    )
                    label.bind(size=label.setter('text_size'))
                    scroll.add_widget(label)
                    text_popup.content = scroll
                    text_popup.open()
                    self.set_status(f"Extracted {len(data)} characters")
                else:
                    self.set_status(data, True)

            self.run_in_thread(
                PDFService.extract_text,
                (path,),
                callback
            )

        extract_btn.bind(on_press=do_extract)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    # ---------- RENAME ----------
    def rename_pdf(self, instance):
        layout = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView()
        layout.add_widget(filechooser)

        name_input = TextInput(
            hint_text="Enter new name (without .pdf)",
            multiline=False,
            size_hint_y=0.1
        )
        layout.add_widget(name_input)

        btn_box = BoxLayout(size_hint_y=0.12, spacing=5)
        cancel_btn = Button(text="Cancel", background_color=(0.8, 0.2, 0.2, 1))
        rename_btn = Button(text="Rename", background_color=(0.2, 0.7, 0.2, 1))
        btn_box.add_widget(cancel_btn)
        btn_box.add_widget(rename_btn)
        layout.add_widget(btn_box)

        popup = Popup(title="Select PDF to Rename", content=layout, size_hint=(0.92, 0.92))

        def do_rename(btn):
            popup.dismiss()
            path = filechooser.path
            new_name = name_input.text.strip()

            if not path:
                self.set_status("Please select a PDF file", True)
                return

            if not new_name:
                self.set_status("Please enter a new name", True)
                return

            def callback(result):
                success, msg = result
                if success:
                    self.set_status(msg)
                else:
                    self.set_status(msg, True)

            self.run_in_thread(
                PDFService.rename,
                (path, new_name),
                callback
            )

        rename_btn.bind(on_press=do_rename)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    VishScanApp().run()