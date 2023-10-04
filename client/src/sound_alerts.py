import simpleaudio as sa
import threading

class SoundPlayback(object):

    def __init__(self, queue):
        thread = threading.Thread(target=self.run, args=())
        self.queue = queue
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def play_sound(self, path):
        wave_obj = sa.WaveObject.from_wave_file(path)
        play_obj = wave_obj.play()
        play_obj.wait_done()

    def run(self):
        while True:
            self.play_sound(self.queue.get())