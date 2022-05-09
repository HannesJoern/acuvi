import sys
import time as tm
import numpy as np
import resampy
import spleeter
from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter
import crepe
from scipy.io.wavfile import write
import math

def audioWorker(mp_queue, mp_queue_vis, mp_queue_audio, RATE, CHUNKSIZE, CHUNKTIME, FPS):
    separator = Separator('spleeter:4stems')
    audio_loader = AudioAdapter.default()
    while(True):
        while mp_queue.empty():
            tm.sleep(0.1)
        
        time_begin = tm.perf_counter()
        
        data = np.array([[0 for i in range(2)] for j in range(CHUNKSIZE)])
        byte_data, audio_input_counter = mp_queue.get()
        np_data = np.frombuffer(byte_data, dtype=np.int16)
        waveform = np.reshape(np_data, (CHUNKSIZE, 2))

        print("audio worker started with audio_input_counter")
        print(audio_input_counter)
        prediction = separator.separate(waveform) 
        
        vocals = prediction['vocals']
        bass = prediction['bass']
        drums = prediction['drums']
        other = prediction['other']

        #for now only once channnel of result is considered

        vocals_mono = vocals[:,0]# / 2 + vocals[:,1] / 2
        bass_mono = bass[:,0]# / 2 + bass[:,1] / 2
        drums_mono = drums[:,0] #/ 2 + drums[:,1] / 2
        other_mono = other[:,0]# / 2 + other[:,1] / 2

        #maybe unnecessary conversions found here

        vocals_mono_abs = np.abs(vocals_mono)
        bass_mono_abs = np.abs(bass_mono)
        other_mono_abs = np.abs(other_mono)
        drums_mono_abs = np.abs(drums_mono)

        vocals_downsampled_temp = np.zeros(300)
        bass_downsampled_temp = np.zeros(300)
        other_downsampled_temp = np.zeros(300)
        drums_downsampled_temp = np.zeros(300)
        for i in range(300):
            vocals_downsampled_temp[i] = np.sum(vocals_mono_abs[i*1470:(i+1)*1470-1])
            bass_downsampled_temp[i] = np.sum(bass_mono_abs[i*1470:(i+1)*1470-1])
            other_downsampled_temp[i] = np.sum(other_mono_abs[i*1470:(i+1)*1470-1])
            drums_downsampled_temp[i] = np.sum(drums_mono_abs[i*1470:(i+1)*1470-1])

        vocals_downsampled = vocals_downsampled_temp/1470
        bass_downsampled = bass_downsampled_temp/1470
        other_downsampled = other_downsampled_temp/1470
        drums_downsampled = drums_downsampled_temp/1470

        #pack up data for visualizer:

        vis_data = np.zeros(4)
        vis_data = np.array([vocals_downsampled, bass_downsampled, other_downsampled, drums_downsampled])
        
        #make data available for other processes:

        mp_queue_audio.put([byte_data, audio_input_counter])
        mp_queue_vis.put([vis_data, audio_input_counter])

        
        #old code that might be recycled:
        """vocals_time, vocals_frequency, vocals_confidence, vocals_activation = crepe.predict(vocals_mono, RATE, model_capacity='tiny', viterbi=True)
        other_time, other_frequency, other_confidence, other_activation = crepe.predict(other_mono, RATE, model_capacity='tiny', viterbi=True)
        bass_time, bass_frequency, bass_confidence, bass_activation = crepe.predict(bass_mono, RATE, model_capacity='tiny', viterbi=True)
        
        
        
        
        vocals_intensity_temp = 0
        other_intensity_temp = 0
        bass_intensity_temp = 0
        drums_intensity_temp = 0
        
        vocals_intensity = np.zeros(FPS*CHUNKTIME)
        other_intensity = np.zeros(FPS*CHUNKTIME)
        bass_intensity = np.zeros(FPS*CHUNKTIME)
        drums_intensity = np.zeros(FPS*CHUNKTIME)
        
        downsampling_factor_intensity = math.floor(RATE/FPS)
        downsampling_factor_frequency = math.floor(vocals_frequency.size/CHUNKTIME/FPS)
        
        for i in range(FPS*CHUNKTIME):
            for j in range(downsampling_factor_intensity):
            
                vocals_intensity_temp += vocals_mono_abs[i*downsampling_factor_intensity + j]
                other_intensity_temp += vocals_mono_abs[i*downsampling_factor_intensity + j]
                bass_intensity_temp += vocals_mono_abs[i*downsampling_factor_intensity + j]
                drums_intensity_temp += vocals_mono_abs[i*downsampling_factor_intensity + j]
                
            vocals_intensity[i] = vocals_intensity_temp
            other_intensity[i] = other_intensity_temp
            drums_intensity[i] = drums_intensity_temp
            bass_intensity[i] = bass_intensity_temp
            
            vocals_intensity_temp = 0
            other_intensity_temp = 0
            bass_intensity_temp = 0
            drums_intensity_temp = 0
            
        vocals_frequency_temp = 0
        other_frequency_temp = 0
        drums_frequency_temp = 0
        bass_frequency_temp = 0
        
        vocals_frequency_downsampled = np.zeros(FPS*CHUNKTIME)
        other_frequency_downsampled = np.zeros(FPS*CHUNKTIME)
        bass_frequency_downsampled = np.zeros(FPS*CHUNKTIME)
        drums_frequency_downsampled = np.zeros(FPS*CHUNKTIME)
            
        for i in range(FPS*CHUNKTIME):
            for j in range(downsampling_factor_frequency):
                vocals_frequency_temp += vocals_frequency[math.floor(i*downsampling_factor_frequency) + j]
                other_frequency_temp += vocals_frequency[math.floor(i*downsampling_factor_frequency) + j]
                bass_frequency_temp += vocals_frequency[math.floor(i*downsampling_factor_frequency) + j]
                drums_frequency_temp += vocals_frequency[math.floor(i*downsampling_factor_frequency) + j]
                
            vocals_frequency_downsampled[i] = vocals_frequency_temp / downsampling_factor_frequency 
            other_frequency_downsampled[i] = other_frequency_temp / downsampling_factor_frequency
            drums_frequency_downsampled[i] = drums_frequency_temp / downsampling_factor_frequency
            bass_frequency_downsampled[i] = bass_frequency_temp / downsampling_factor_frequency
            
            vocals_frequency_temp = 0
            other_frequency_temp = 0
            drums_frequency_temp = 0
            bass_frequency_temp = 0
            
            
        print('vocals frequency max:')
        print(np.max(vocals_mono))
        print('other frequency max')
        print(np.max(other_mono))
        print('vocals_frequency length')
        print(vocals_frequency.size)
        
        print('time for audio loop:')"""




        time_end = tm.perf_counter()
        print(time_end - time_begin)


    
    return

  
