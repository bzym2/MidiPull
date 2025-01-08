import time
import tkinter as tk
from tkinter import messagebox
import rtmidi
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF
import mido
from mido import MidiFile, MidiTrack, Message
import threading
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(),  # 输出到控制台
                        logging.FileHandler('midi_receiver.log')  # 输出到文件
                    ])

class MidiPull:
    def __init__(self, master):
        self.master = master
        self.master.title("MIDIPull Application")

        self.running = False
        self.midi_in = None
        self.midi_file = None
        self.track = None

        self.start_button = tk.Button(master, text="Start", command=self.start_receiving)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_receiving, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

    def start_receiving(self):
        if not self.running:
            logging.info("Starting MIDI reception...")
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.midi_in = rtmidi.MidiIn()
            self.midi_in.open_port(0)
            self.midi_file = MidiFile()
            self.track = MidiTrack()
            self.midi_file.tracks.append(self.track)
            self.thread = threading.Thread(target=self.receive_midi)
            self.thread.start()

    def stop_receiving(self):
        if self.running:
            logging.info("Stopping MIDI reception...")
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.midi_in.close_port()
            self.midi_in = None
            self.save_midi_file()
            messagebox.showinfo("Info", "MIDI recording stopped and saved.")

    def receive_midi(self):
        last_time = time.time()
        while self.running:
            msg = self.midi_in.get_message()
            if msg:
                current_time = time.time()
                delta_time = int((current_time - last_time) * 960) # 正常应该是480，但我这里录出来是快了一倍，所以改成960
                last_time = current_time
                midi_msg = Message.from_bytes(msg[0])
                midi_msg.time = delta_time
                self.track.append(midi_msg)
                logging.debug(f"Received and saved MIDI message: {midi_msg}")

    def save_midi_file(self):
        logging.info("Saving MIDI file...")
        self.midi_file.save('output.mid')
        self.track = None
        self.midi_file = None
        logging.info("MIDI file saved.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MidiPull(root)
    root.mainloop()