from shlex import join
import numpy as np
from sharedFunctions import *
import scipy
import math
import crepe
import matplotlib.pyplot as plt

class Visualizer():
    def __init__(self, RATE, CHUNKSIZE, CHUNKTIME, FPS, NUM_PIXELS):
        self.RATE = RATE
        self.CHUNKSIZE = CHUNKSIZE
        self.CHUNKTIME = CHUNKTIME
        self.FPS = FPS
        self.NUM_PIXELS = NUM_PIXELS
        self.max_rgb = 255

        self.x_squares = 150
        self.y_squares = 2
        self.drums_length = 30
        self.col_coeff=500
        self.empty_color_val = "#%02x%02x%02x" % (0, 0, 0) #for rgb display
        #for LED Leiste self.empty_color_val = "0X000000" 
        self.len_vis = FPS*CHUNKTIME #size of chunk of vis_samples
        self.prev_intensities = np.array([[[0 for i in range(self.len_vis)] for j in range(2)] for k in range(4)])
        self.r_down = RATE/FPS #downsampling rate
        init_norm_factor = 150 #normalization factor
        self.norm_factors = {"low_drums": 1/500 , "high_drums" : 1/100, "vocals": init_norm_factor, "other": init_norm_factor, "bass": init_norm_factor}

        #temporary variables:
        self.prev_row_low_drums =  np.array([[0 for i in range(3)] for j in range(self.x_squares)])
        self.prev_row_high_drums = np.array([[0 for i in range(3)] for j in range(self.x_squares)])

        self.prev_line_low_drums =  np.array([[0 for i in range(3)] for j in range(self.drums_length)])
        self.prev_line_high_drums = np.array([[0 for i in range(3)] for j in range(self.drums_length)])
        self.value_low_right_prev = 0
        self.value_low_left_prev = 0
        self.value_high_right_prev = 0
        self.value_high_left_prev = 0
    def visualize(self, spleeter_data):

    
        visualization = np.array([[self.empty_color_val for i in range(self.NUM_PIXELS)] for j in range(self.len_vis)])

        """square_visualization = np.array([[[self.empty_color_val for x in range(self.x_squares)] for y in range(self.y_squares)] for j in range(self.len_vis)])

        #drums visualization pipeline
        for i in range(self.len_vis):
            #get sample
            start = int(i*self.r_down)
            stop = int((i+1)*self.r_down-1)
            drums_sample_left = spleeter_data['drums'][start:stop,0]
            drums_sample_right = spleeter_data['drums'][start:stop,1]
            #apply visualization algorithm
            row_low_drums, row_high_drums = self.visualize_drum_sample(drums_sample_left, drums_sample_right)
            #update temporal samples
            self.prev_row_low_drums = row_low_drums
            self.prev_row_high_drums = row_high_drums

            #put into visualization
            visualization[i][0:self.drums_length] = self.rgbToHexRow(row_low_drums)
            visualization[i][149- self.drums_length, 149] = self.rgbToHexRow(row_low_drums)
            square_visualization[i][self.y_squares - 2] = self.rgbToHexRow(row_high_drums)
            square_visualization[i][self.y_squares - 1] = self.rgbToHexRow(row_low_drums)
            flattened_square_vis = square_visualization[i].flatten()
            visualization[i][0:flattened_square_vis.size] = flattened_square_vis"""

        #other visualization pipeline with crepe:
        bass_right = spleeter_data['bass'][:,0]
        other_right = spleeter_data['other'][:,0]
        vocals_right = spleeter_data['vocals'][:,0]
        hopsize = self.CHUNKTIME*1000/(self.len_vis-1)
        time, bass_frequency, confidence, bass_activation = crepe.predict(bass_right, self.RATE, viterbi = True, model_capacity='small', step_size=hopsize)
        time, other_frequency, confidence, other_activation = crepe.predict(other_right, self.RATE, viterbi = True, model_capacity='small', step_size=hopsize)
        time, other_frequency, confidence, vocals_activation = crepe.predict(other_right, self.RATE, viterbi = True, model_capacity='small', step_size=hopsize)
        if bass_frequency.size != self.len_vis:
            print("hop size in crepe is defined wrong")

        #initialize keyboard visualization:
        
        keyboard_visualization = np.array([[self.empty_color_val for k in range(120)] for j in range(self.len_vis)])
        for i in range (self.len_vis):
            #for j in range(keyboard_visualization[i].size):
                #if keyboard_visualization[i-1][j][0] > 0:
                 #   keyboard_visualization[i][j][0] = int(keyboard_visualization[i][j][0]*0.8)
            temp_bass = 0
            temp_other = 0
            temp_vocals = 0
            prev_temp_bass = 0
            prev_temp_other = 0
            prev_temp_vocals = 0
            for j in range(120):
                for k in range(3):
                    temp_bass += bass_activation[i][j*k+k]
                    temp_other += other_activation[i][j*k+k]
                    temp_vocals += vocals_activation[i][j*k+k]

                temp_bass = temp_bass * self.norm_factors['bass']
                temp_other = temp_other * self.norm_factors['other']
                temp_vocals = temp_vocals * self.norm_factors['vocals']

                temp_factor = 0.75

                temp_bass += prev_temp_bass * temp_factor
                temp_other += prev_temp_other * temp_factor
                temp_vocals += prev_temp_vocals * temp_factor

                #if(temp_bass > 200):
                #    self.norm_factors['bass'] = 200/temp_bass
                #if(temp_other > 200):
                #    self.norm_factors['other'] = 200/temp_other
                #if(temp_vocals > 200):
                #    self.norm_factors['vocals'] = 200/temp_vocals
                            

                keyboard_visualization[i][j] = "#%02x%02x%02x" % (int(temp_vocals), int(temp_other), int(temp_bass))
                prev_temp_bass = temp_bass
                prev_temp_other = temp_other
                prev_temp_vocals = temp_vocals
            
                temp_bass = 0
                temp_other = 0
                temp_vocals = 0
            
            """bass_key = int(round(self.freq_to_piano_key(bass_frequency[i])))
            other_key = int(round(self.freq_to_piano_key(other_frequency[i])))

            start = int(i*self.r_down)
            stop = int((i+1)*self.r_down-1)
            bass_sample_left = spleeter_data['bass'][start:stop,0]
            other_sample_left = spleeter_data['other'][start:stop,0]
            if np.any(bass_sample_left):
                bass_intensity = np.max(bass_sample_left)
            else:
                bass_intensity = 0
            if np.any(other_sample_left):
                other_intensity = np.max(other_sample_left)
            else:
                other_intensity = 0

            bass_intensity = int(self.norm_factors['bass'] * bass_intensity)
            if bass_intensity > 254:
                self.norm_factors['bass'] = 254/bass_intensity

            #keyboard_visualization[i][bass_key] = "#%02x%02x%02x" % (bass_intensity, 0, 0)

            other_intensity = int(self.norm_factors['other'] * other_intensity)
            if other_intensity > 254:
                self.norm_factors['other'] = 254/other_intensity
            
            keyboard_visualization[i][other_key] = "#%02x%02x%02x" % (0, other_intensity, 0)"""

            visualization[i][:120] = keyboard_visualization[i]


        #drums visualization pipeline
        for i in range(self.len_vis):
            #get sample
            start = int(i*self.r_down)
            stop = int((i+1)*self.r_down-1)
            drums_sample_left = spleeter_data['drums'][start:stop,0]
            drums_sample_right = spleeter_data['drums'][start:stop,1]
            #apply visualization algorithm
            line_low_drums, line_high_drums = self.visualize_drum_sample_in_lines(drums_sample_right)
            #update temporal samples
            self.prev_line_low_drums = line_low_drums
            self.prev_line_high_drums = line_high_drums

            #put into visualization
            visualization[i][0:self.drums_length] = self.rgbToHexLine(line_low_drums)
            visualization[i][149- self.drums_length:149] = self.rgbToHexLine(line_high_drums)
        #array of 300 processed vis_samples
        return visualization


        #self.prev_intensities = intensities - used for temporal bluring
            

    #emas drums visualizer
    def visualize_drum_sample(self, spleeter_sample_left, spleeter_sample_right):
        max_value = int(self.x_squares/2)
        values_left = self.calculateDrumValues(spleeter_sample_left, self.value_low_left_prev, self.value_high_left_prev, max_value)
        values_right = self.calculateDrumValues(spleeter_sample_right, self.value_low_right_prev, self.value_high_right_prev, max_value)
        self.value_low_right_prev = values_right[0]
        self.value_high_right_prev = values_right[1]
        self.value_low_left_prev = values_left[0]
        self.value_high_left_prev = values_left[1]
        
        line_low = self.createRGBDrumRow(values_left[0], values_right[0], max_value, self.prev_row_low_drums)
        line_high = self.createRGBDrumRow(values_left[1], values_right[1], max_value, self.prev_row_high_drums)
        return line_low, line_high

    def visualize_drum_sample_in_lines(self, spleeter_sample_right):
        max_value = self.drums_length - 1
        values_right = self.calculateDrumValues(spleeter_sample_right, self.value_low_right_prev, self.value_high_right_prev, max_value)
        self.value_low_right_prev = values_right[0]
        self.value_high_right_prev = values_right[1]
        
        line_low = self.createRGBDrumLowLine(values_right[0], max_value, self.prev_row_low_drums)
        line_high = self.createRGBDrumHighLine(values_right[1], max_value, self.prev_row_high_drums)
        return line_low, line_high

    def calculateDrumValues(self, spleeter_data_sample, value_low_prev, value_high_prev, max_value):
        if not np.any(spleeter_data_sample):
            return np.array([0, 0])
        else:
            drum_pivot = 600
            if self.col_coeff<1:
                raise ValueError('col_coeff has to be greater or equal than one')

            fft_data = scipy.fftpack.rfft(spleeter_data_sample)
            for i in fft_data:
                i = abs(i)
            step = self.RATE/len(spleeter_data_sample)
            sum_l = max(fft_data[:int(drum_pivot/step)])
            sum_h = max(fft_data[int(drum_pivot/step):int(10000/step)])

            #adaptive normalization factor finding:
            value_low = sum_l * self.norm_factors["low_drums"]
            if value_low > self.drums_length:
                self.norm_factors["low_drums"] = max_value/sum_l
            value_low = self.val(value_low, max_value, 1)

            value_high = sum_h * self.norm_factors["high_drums"]
            if value_high > self.drums_length:
                self.norm_factors["high_drums"] = max_value/sum_h
            value_high = self.val(value_high, max_value, 1)


            if value_low < value_low_prev:
                value_low = value_low_prev - 1
            if value_high < value_high_prev:
                value_high = value_high_prev - 1

            res = np.array([value_low, value_high])
        return res

    def createRGBDrumHighLine(self, value, max_value, prev_line):
        row = np.array([[0 for i in range(3)] for j in range(self.drums_length)])
        for i in range(max_value):
            if i < value:
                row[max_value - 1 - i] = np.array([int((254/self.drums_length-1)*(max_value - i)),int((254/self.drums_length-1)*(max_value - i)),int((254/self.drums_length-1)*(max_value - i))])
            else:
                color = prev_line[max_value - 1 - i]
                row[max_value - 1 - i] = np.array([int((color[0]) / self.col_coeff), int((color[1]) / self.col_coeff), int((color[2]) / self.col_coeff)])
        return row

    def createRGBDrumLowLine(self, value, max_value, prev_line):
        row = np.array([[0 for i in range(3)] for j in range(self.drums_length)])
        for i in range(max_value):
            if i < value:
                row[i] = np.array([int((254/self.drums_length-1)*(max_value - i)),int((254/self.drums_length-1)*(max_value - i)),int((254/self.drums_length-1)*(max_value - i))])
            else:
                color = prev_line[i]
                row[i] = np.array([int((color[0]) / self.col_coeff), int((color[1]) / self.col_coeff), int((color[2]) / self.col_coeff)])
        return row

    def createRGBDrumRow(self, value_left, value_right, max_value, prev_row):
        row = np.array([[0 for i in range(3)] for j in range(self.x_squares)])

        for i in range(max_value):
            if i < value_left:
                row[max_value - 1 - i] = np.array([int((254/11)*i),0,204])
            else:
                color = prev_row[max_value - 1 - i] # be wary here is a mistake!!!
                row[max_value - 1 - i] = np.array([255 - int((255 - color[0]) / self.col_coeff), 255 - int((255 - color[1]) / self.col_coeff), 255 - int((255 - color[2]) / self.col_coeff)])

            if i < value_right:
                row[max_value + i] = np.array([int((254/11)*i),0,204])
            else:
                color = prev_row[max_value + i]
                row[max_value + i] = np.array([255 - int((255 - color[0]) / self.col_coeff), 255 - int((255 - color[1]) / self.col_coeff), 255 - int((255 - color[2]) / self.col_coeff)])
        return row

    #Updating-Normalization-Factor-Finding-Function that always adjusts to highest observed value in each session, starting with normfac_init
    def update_norm_factor(self, k, max):
        if self.norm_factors[k]*max > self.max_rgb:
            self.norm_factors[k] = self.max_rgb/max

    #normalization function
    def normalize(self, intensities):
        for k in range(4):
            self.update_norm_factor(k, np.amax(intensities[k]))
            intensities[k] = intensities[k] * self.norm_factors[k]
        return intensities

    #tempural blurring
    def apply_temp_blur(self, intensities):
        # iterate through audio channels
        for k in range(4):
            # iterate through r/l:
            for j in range(2):
                # iterate through visual samples
                    for i in range(self.len_vis):
                            #temporal blurring
                            if i > 0:    
                                if intensities[k][j][i-1] > intensities[k][j][i]:
                                    intensities[k][j][i] = intensities[k][j][i-1]*0.8
                            if i == 0:
                                if self.prev_intensities[k][j][self.len_vis-1] > intensities[k][j][i]:
                                    intensities[k][j][i] = self.prev_intensities[k][j][self.len_vis-1]*0.8

        return intensities

    #downsampling from audio RATE to visualization FPS
    def sample_down(self, spleeter_data):
        intensities = np.array([[[0 for i in range(self.len_vis)] for j in range(2)] for k in range(4)])
        # iterate through audio channels
        for k in range(4):
            # iterate through r/l:
            for j in range(2):
                # iterate through visual samples
                    for i in range(self.len_vis):
                        # first need to check if there is anything nonzero
                        if np.any(spleeter_data[k][j][int(i*self.r_down):int((i+1)*self.r_down-1)]):
                            # to then find the maximum. this is a vis_sample
                            intensities[k][j][i] = int(np.max(spleeter_data[k][j][int(i*self.r_down):int((i+1)*self.r_down-1)]))
        #array of 300 raw vis_samples
        return intensities



    def val(self,value,max,threshold):
        if value>max:
            value=max
        if value<threshold:
            return 1
        return value

    def rgbToHexRow(self, row):
        hex_row = np.array([self.empty_color_val for i in range(self.x_squares)])
        for i in range(self.x_squares):
            #hex_row[i] = rgb_to_hex(row[i][0], row[i][1], row[i][2])
            hex_row[i] = "#%02x%02x%02x" % (row[i][0], row[i][1], row[i][2]) #for RGBdisplay
        return hex_row

    def rgbToHexLine(self, line):
        hex_line = np.array([self.empty_color_val for i in range(self.drums_length)])
        for i in range(self.drums_length):
            #hex_row[i] = rgb_to_hex(row[i][0], row[i][1], row[i][2])
            hex_line[i] = "#%02x%02x%02x" % (line[i][0], line[i][1], line[i][2]) #for RGBdisplay
        return hex_line
    def sigmoid(self, value):
        x = value
        y = 254 / 1 + math.exp(-15*x + 10)
        return y

    def hex_to_rgb(hex):
        rgb = []
        for i in (0, 2, 4):
            decimal = int(hex[i:i+2], 16)
            rgb.append(decimal)
        return np.array(rgb)
    
    def freq_to_piano_key(self, freq):
        key = 12 * np.log2(freq/440) + 49
        return key