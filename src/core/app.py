import sys
from src.core.gui import WavPatcherGUI
from src.core.wav_processor import WavProcessor

class WavPatcherApp:
    def __init__(self):
        self.processor = WavProcessor(
            status_callback=self._on_status_update,
            progress_callback=self._on_progress_update
        )

        self.gui = WavPatcherGUI(
            on_browse=self._on_browse,
            on_run=self._on_run,
            on_ro_check=self._on_ro_check,
            on_convert=self._on_convert,
            on_browse_click2=self._on_browse_click2
        )

        self.selected_directory = ""
        self.selected_directory2 = ""
        self.simulate_mode = True

    def _on_browse(self):
        directory = self.gui.browse_for_directory()
        if directory:
            self.selected_directory = directory
            total_files = self.processor.count_total_files(directory)

            if total_files == 0:
                self.gui.update_text_area("No *.wav files could be found!", append=True)
                self.gui.enable_run_button(False)
            else:
                self.gui.update_text_area(f"{total_files} *.wav files will be scanned.", append=True)
                self.gui.enable_run_button(True)

    def _on_browse_click2(self):
        directory = self.gui.browse_for_directory2()
        if directory:
            self.selected_directory2 = directory
            total_files = self.processor.count_total_files(directory)

            if total_files == 0:
                self.gui.update_text_area2("No *.wav files could be found!", append=True)
                self.gui.enable_convert_button(False)
            else:
                self.gui.update_text_area2(f"{total_files} *.wav files will be scanned for high bit depth.", append=True)
                self.gui.enable_convert_button(True)

    def _on_run(self):
        if self.selected_directory:
            self.gui.set_button_states(False)
            self.processor.start_processing_thread(
                self.selected_directory,
                self.simulate_mode,
                completion_callback=self._on_processing_complete
            )

    def _on_processing_complete(self, result):
        self.gui.set_button_states(True)

    def _on_ro_check(self, is_readonly):
        self.simulate_mode = is_readonly

    def _on_status_update(self, message):
        if self.notebook_current_tab() == 0:
            self.gui.update_text_area(message, append=True)
        else:
            self.gui.update_text_area2(message, append=True)

    def _on_progress_update(self, message):
        if self.notebook_current_tab() == 0:
            self.gui.update_status(message)
        else:
            self.gui.update_status2(message)

    def notebook_current_tab(self):
        try:
            return self.gui.notebook.index(self.gui.notebook.select())
        except:
            return 0

    def _on_convert(self):
        if self.selected_directory2:
            self.gui.set_button_states2(False)
            self.processor.start_high_bit_depth_thread(
                self.selected_directory2,
                completion_callback=self._on_conversion_complete
            )

    def _on_conversion_complete(self, result):
        self.gui.set_button_states2(True)
        processed_files, high_bit_depth_files = result
        self.gui.update_text_area2(f"\n\nProcessed {processed_files} files, found {high_bit_depth_files} high bit depth files.", append=True)

    def run(self):
        self.gui.start()
        sys.exit()
