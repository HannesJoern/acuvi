
from scipy.io import wavfile

class wav_4_stems:
    def __init__(self,path) -> None:
        self.samplerate, dataVocals = wavfile.read(path+'\\vocals.wav')
        samplerate, dataBass = wavfile.read(path+'\\bass.wav')
        samplerate, dataDrums = wavfile.read(path+'\\drums.wav')
        samplerate, dataOther = wavfile.read(path+'\\other.wav')
        self.data = [dataVocals, dataBass, dataDrums, dataOther]

    def getFrames(self,frames: int,position: int):
        vocals = []
        bass = []
        drums = []
        other = []
        #print(position)
        for i in range(position, min(position+frames,len(self.data[0]))):
            vocals.append((self.data[0][i][0]/32768)*128)
            bass.append((self.data[1][i][0]/32768)*128)
            drums.append((self.data[2][i][0]/32768)*128)
            other.append((self.data[3][i][0]/32768)*128)
        position = position + frames
        return [vocals, bass, drums, other], position










