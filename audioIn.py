"""Captures live audio from the system's default input device and streams raw PCM
chunks into a multiprocessing queue for the visualization process to consume.
"""

import time as tm

import pyaudio


class AudioIn:
    """Opens a PyAudio input stream and pushes incoming audio chunks onto a queue."""

    def __init__(self, RATE, RATE_INTENSITY, audio_in_queue, audio_out_queue):
        self.RATE = RATE
        self.CHUNKSIZE = RATE / RATE_INTENSITY
        self.audio_in_queue = audio_in_queue
        self.audio_out_queue = audio_out_queue

    def audioInWorker(self):
        """Open the audio input stream and block forever while it runs in the background
        (PyAudio delivers data via the `callbackIn` callback, not a return value here).

        NOTE: input_device_index is hardcoded to device 11. Run `pyaudio.PyAudio().get_device_count()`
        with a short device-listing script to find the right index for your system, or make this
        configurable if you need to run acuvi on a different machine.
        """
        self.pIn = pyaudio.PyAudio()
        self.streamIn = self.pIn.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            stream_callback=self.callbackIn,
            frames_per_buffer=int(self.CHUNKSIZE),
            input_device_index=11,
        )
        self.streamIn.start_stream()

        # The stream runs on its own callback thread; this loop just keeps the
        # process alive. Use terminate() below to shut it down cleanly.
        while True:
            tm.sleep(0.5)

    def terminate(self):
        """Stop and close the audio stream. Called on shutdown (e.g. Ctrl+C)."""
        self.streamIn.stop_stream()
        self.streamIn.close()
        self.pIn.terminate()

    def callbackIn(self, in_data, frame_count, time_info, status):
        """PyAudio callback: forward each incoming chunk of raw audio onto the queue."""
        self.audio_in_queue.put(in_data)
        return (in_data, pyaudio.paContinue)
