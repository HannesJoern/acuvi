import time as tm
import multiprocess
from multiprocess import Process, Queue
from audioWorker import audioWorker


def audioWorkerHandler(mp_queue, mp_queue_vis, mp_queue_audio, RATE, CHUNKSIZE, CHUNKTIME, FPS):
          
        audio_worker = Process(target=audioWorker, args=(mp_queue, mp_queue_vis, mp_queue_audio, RATE, CHUNKSIZE, CHUNKTIME, FPS,))
        audio_worker.start()

   
        audio_worker.join()

        
        
        
        
    