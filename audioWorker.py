import time as tm

import audioProcessor
import visualizer



def audioWorker(audio_in_queue, visual_data_queue, audio_out_queue, RATE, CHUNKSIZE, CHUNKTIME, FPS, NUM_PIXELS):

    audio_processor = audioProcessor.AudioProcessor(RATE, CHUNKSIZE, CHUNKTIME)
    visual_processor = visualizer.Visualizer(RATE, CHUNKSIZE, CHUNKTIME, FPS, NUM_PIXELS)

    while(True):
        #wait for callback-in function to deliver us new data
        while audio_in_queue.empty():
            tm.sleep(0.1)
        
        #performance counter to see how fast our entire data processing is
        time_begin = tm.perf_counter()
        
        #get data from audio input stream
        byte_data, audio_input_counter = audio_in_queue.get()

        print("audio worker started with audio_input_counter" + str(audio_input_counter))

        #use spleeter
        prediction = audio_processor.separate(byte_data)
        
        #visualize
        visualization = visual_processor.visualize(prediction)

        #give audio output available to output stream
        audio_out_queue.put([byte_data, audio_input_counter])

        #give visual data avialable to display
        visual_data_queue.put([visualization, audio_input_counter])

        #display performance
        time_end = tm.perf_counter()
        print("audio worker finished with time: " + str(time_end - time_begin))

    return

  
