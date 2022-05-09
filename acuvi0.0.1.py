from audioWorker import audioWorker
from audioWorkerHandler import audioWorkerHandler
from visOutput import visOutput
if __name__ == '__main__':
    import multiprocess
    #from multiprocess import shared_memory
    from multiprocess import Process, Queue
    import time as tm
    import collections
    import resampy
    


    import pyaudio
    import numpy as np

    RATE=44100
    CHUNKTIME = 10
    CHUNKSIZE = RATE*CHUNKTIME
    FPS = 30

    audioFrame = collections.deque(maxlen=10)
    #audioFrameCopy = collections.deque(maxlen=10)

    #shm_content = np.array([[0 for j in range(CHUNKSIZE)] for k in range(11)])
    #shm_audio = shared_memory.SharedMemory(create=True, size=shm_content.nbytes)
    #shm_numpy = np.ndarray(shm_content.shape, dtype=shm_content.dtype, buffer=shm_audio.buf)
    #shm_numpy[:] = shm_content[:]

    #output_counter = 0
    audio_input_counter = 0

    mp_queue = Queue()
    mp_queue_vis = Queue()
    mp_queue_audio = Queue()
    mp_queue_delay = Queue()
    #wf = wave.open(r'C:\Users\Hannes\OneDrive\acuvi\baiana.wav')

    pIn = pyaudio.PyAudio()
    pOut = pyaudio.PyAudio()

    def callbackIn(in_data, frame_count, time_info, status):
        global audioFrame, audio_input_counter

        #audioFrame.append((in_data, audio_input_counter))
        
        mp_queue.put((in_data, audio_input_counter))
        print('append successful, input counter: ' + str(audio_input_counter))
        audio_input_counter = (audio_input_counter + 1) % 100
        return (in_data, pyaudio.paContinue)
        
    def callbackOut(in_data, frame_count, time_info, status):
        global audioFrame, wf, mp_queue_delay, mp_queue_audio
        while mp_queue_audio.empty():
            #print("audio callback has nothing to do")
            tm.sleep(0.05)
        #data, output_counter = audioFrame.pop()
        data, output_counter = mp_queue_audio.get()
        print("playback pop successful, with output counter:" + str(output_counter))
        mp_queue_delay.put([tm.time(), output_counter])
        
        return (data, pyaudio.paContinue)


    def main():
        if __name__ == '__main__':
            multiprocess.freeze_support()
            streamIn = pIn.open(format=pyaudio.paInt16, channels=2, rate=RATE, input=True, stream_callback=callbackIn, frames_per_buffer=CHUNKSIZE)
            streamOut = pOut.open(format=pyaudio.paInt16, channels=2, rate=RATE, output=True, stream_callback=callbackOut, frames_per_buffer=CHUNKSIZE)

            streamIn.start_stream()
            audio_worker_handler = Process(target=audioWorkerHandler, args=(mp_queue, mp_queue_vis, mp_queue_audio, RATE, CHUNKSIZE, CHUNKTIME, FPS,))
            audio_worker_handler.start()
            vis_worker = Process(target=visOutput, args=(mp_queue, mp_queue_vis, mp_queue_delay, RATE, CHUNKSIZE, CHUNKTIME, FPS,))
            vis_worker.start()


            tm.sleep(10)

            streamOut.start_stream()

            #wait for stream to finish
           
            while(streamIn.is_active()):
                
                tm.sleep(2)
                
            streamIn.stop_stream()
            streamOut.stop_stream()
            streamIn.close()
            streamOut.close()
            audio_worker_handler.join()
            vis_worker.join()
            pIn.terminate()
            pOut.terminate()
            
    if __name__ == '__main__':
        multiprocess.freeze_support()
        main()
