import youtube_downloader
import wav_converter
import os

class youtube_stream:
    def __init__(self) -> None:        
        self.convert_queue = []
        self.youtube_downloader = youtube_downloader.youtube_downloader()

    #input is an url and this method downloads the youtube video corresponding to the url and saves it in downloaded_files,
    #the file name and the extension type are saved in the "convert_queue" awaiting to be converted to a wav file
    def add_from_url(self, url):
        self.youtube_downloader.add_from_url_in_queue(url)
        file_info = self.youtube_downloader.download()
        self.convert_queue.append(file_info)

    #works like the method above but accepts a generic search term
    def add_from_title(self, title):
        self.youtube_downloader.add_from_title_in_queue(title)
        file_info = self.youtube_downloader.download()
        self.convert_queue.append(file_info)

    #converts the first file in the convert queue into a wav file, puts it in "downloaded_files"
    def convert_to_wav(self):
        file_info = self.convert_queue.pop(0)
        wav_converter.convert_file(name=file_info[0],extension_input=file_info[1],extensoin_output='wav')
    
    #removes files at index "index" of the list downloaded_files in youtube_downloader
    def remove_file(self,index):
        file_info = self.youtube_downloader.remove_downloaded_file_from_list(index)
        os.remove("C:\\Users\\emhz\\Documents\\Python\\acuvi\\audio_input\\wav_files\\" + file_info[0] + ".wav")
        os.remove("C:\\Users\\emhz\\Documents\\Python\\acuvi\\audio_input\\downloaded_files\\" + file_info[0] + "." + file_info[1])
    
        

    