import youtube_downloader
import wav_converter
import os
import pygame

class youtube_stream:
    def __init__(self,path) -> None:        
        self.path = path

        self.convert_queue = []
        self.youtube_downloader = youtube_downloader.youtube_downloader(path)
        self.is_playing = False
        self.is_paused = False
        self.pygame_instance = pygame.mixer.init()

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
        os.remove(self.path+"\\wav_files\\" + file_info[0] + ".wav")
        os.remove(self.path+"\\downloaded_files\\" + file_info[0] + "." + file_info[1])

    #prints a list of all the files that are downloaded
    def print_downloaded_files(self):
        length = len(self.youtube_downloader.downloaded_file_names)
        if length == 0:
            print('no downloaded files found')
            return
        for i in range(length):
            print(str(i)+". " + self.youtube_downloader.downloaded_file_names[i][0])
    
    def play_file(self, index):
        file_info = self.youtube_downloader.downloaded_file_names[index]
        pygame.mixer.stop()
        s = pygame.mixer.Sound(self.path+"\\wav_files\\"+file_info[0]+"."+"wav")
        s.play()
        self.is_playing=True
        self.is_paused = False

    def pause_playing_file(self):
        if self.is_playing:
            if not self.is_paused:
                pygame.mixer.pause()
                self.is_paused = True
            else:
                print('music alrady paused')
        else:
            print('there is no music to be paused')

    def resume_playing_file(self):
        if self.is_playing:
            if self.is_paused:
                pygame.mixer.unpause()
                self.is_paused = False
            else:
                print('musci si playing')
        else:
            print('there is no music to be unpaused')

    def stop_playing_file(self):
        if self.is_playing:
            pygame.mixer.stop()
            self.is_playing = False
        else:
            print('there is no music to be stopped')

        

    