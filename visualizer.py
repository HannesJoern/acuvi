
class visualizer:
    def __init__(self) -> None:
        col = "#%02x%02x%02x" % (255, 255, 255)
        self.vocals_arr = [col]*75
        self.other_arr = [col]*75
        self.drums_arr = [col]*75
        self.bass_arr = [col]*75


    def update_rgb_array(self,vocals,drums,bass,other):
        max_vocals = int(max(vocals))*5
        max_bass = int(max(bass))*5
        max_drums = int(max(drums))*5
        max_other = int(max(other))*5
        vocals_rgb = "#%02x%02x%02x" % (255, 255-max_vocals, 255-max_vocals) if max_vocals<=255 else "#%02x%02x%02x" % (255, 0, 0) if max_vocals > 50 else "#%02x%02x%02x" % (255, 255, 255)
        bass_rgb = "#%02x%02x%02x" % (255-max_bass, 255, 255-max_bass) if max_bass<=255 else "#%02x%02x%02x" % (0, 255, 0) if max_bass > 50 else "#%02x%02x%02x" % (255, 255, 255)
        drums_rgb = "#%02x%02x%02x" % (255-max_drums, 255-max_drums, 255) if max_drums<=255 else "#%02x%02x%02x" % (0, 0, 255) if max_drums > 50 else "#%02x%02x%02x" % (255, 255, 255)
        other_rgb = "#%02x%02x%02x" % (255, 255-max_other, 255) if max_other<=255 else "#%02x%02x%02x" % (255, 0, 255) if max_other > 50 else "#%02x%02x%02x" % (255, 255, 255)
        self.vocals_arr.insert(0,vocals_rgb)
        self.other_arr.insert(0,other_rgb)
        self.bass_arr.insert(0,bass_rgb)
        self.drums_arr.insert(0,drums_rgb)
        self.vocals_arr.pop(75)
        self.bass_arr.pop(75)
        self.drums_arr.pop(75)
        self.other_arr.pop(75)
        self.vocals_arr.insert(0,vocals_rgb)
        self.other_arr.insert(0,other_rgb)
        self.bass_arr.insert(0,bass_rgb)
        self.drums_arr.insert(0,drums_rgb)
        
        self.vocals_arr.pop(75)
        self.bass_arr.pop(75)
        self.drums_arr.pop(75)
        self.other_arr.pop(75)
        
        return self.vocals_arr + self.other_arr + self.bass_arr + self.drums_arr
