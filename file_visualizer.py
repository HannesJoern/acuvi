import RGB_display
import aubio
import time

class visualizer:
    def __init__(self, SAMPLERATE, separated_data,starting_time):
        self.starting_time = starting_time
        self.separated_data = separated_data
        self.SAMPLERATE = SAMPLERATE
        self.rgb = RGB_display.RGB_display(24,12)
        self.rgb.createRgbDisplay()
        self.pitchdetector = aubio.pitch("yin", buf_size=1536, samplerate=SAMPLERATE, hop_size=1536)
        self.pitchdetector.set_tolerance(0.8)
        self.prev_r_l = 0
        self.prev_r_h = 0
        self.prev_o = 0
        self.prev_v = 0

    def visualize(self):
        while True:
            startime = time.time()
            start_sample = int((time.time()-self.starting_time)*self.SAMPLERATE)
            data = self.separated_data.get_samples(1536,start_sample)
            print(len(data[0]))
            if len(data[0]) == 1536:
                self.separated_data.clear_used_data()

                voice = data[0]
                bass = data[1]
                drums = data[2]
                other = data[3]
                self.prev_r_l, self.prev_r_h = self.rgb.drums(drums,self.SAMPLERATE,self.prev_r_l,self.prev_r_h,5)
                self.rgb.bass(bass,self.pitchdetector,sr=self.SAMPLERATE)
                self.prev_v = self.rgb.other(voice,self.prev_v)
                self.prev_o = self.rgb.otherv2(other,self.prev_o)
                self.rgb.update()

                if time.time()-startime < 1536/self.SAMPLERATE :
                    time.sleep( (1536/self.SAMPLERATE) - time.time()-startime)
            else:
                time.sleep(0.5)