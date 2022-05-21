import time as tm

import audioProcessor
import visualizer
import separated_data


def audioWorker(audio_in_queue, audio_out_queue, data_buffer, RATE, CHUNKSIZE, CHUNKTIME, FPS, NUM_PIXELS):

    audio_processor = audioProcessor.AudioProcessor(RATE, CHUNKSIZE, CHUNKTIME)
    visual_processor = visualizer.Visualizer(RATE, CHUNKSIZE, CHUNKTIME, FPS, NUM_PIXELS)

    while(True):
        #wait for callback-in function to deliver us new data
        while audio_in_queue.empty():
            tm.sleep(0.1)
        
        #performance counter to see how fast our entire data processing is
        time_begin = tm.time()
        
        #get data from audio input stream
        byte_data, audio_input_counter = audio_in_queue.get()

        print("audio worker started with audio_input_counter" + str(audio_input_counter))

        #use spleeter
        prediction = audio_processor.separate(byte_data)
        data_buffer.put(prediction)
        #print("length of buffer: " + str(len(data_buffer.data['vocals'])))
        #visualize
        visualization = visual_processor.visualize(prediction)

        #give audio output available to output stream
        audio_out_queue.put([byte_data, audio_input_counter])

        #display performance
        time_end = tm.time()
        print("audio worker finished with time: " + str(time_end - time_begin))





  
