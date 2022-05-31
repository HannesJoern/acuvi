import youtube_downloader
import os
import pygame
import threading
import file_separator

class youtube_stream:
    def __init__(self,path) -> None:        
        self.path = path
        self.youtube_downloader = youtube_downloader.youtube_downloader(path)
        self.is_playing = False
        self.is_paused = False
        self.pygame_instance = pygame.mixer.init()

    #input is an url and this method downloads the youtube video corresponding to the url and saves it in downloaded_files,
    #the file name and the extension type are saved in the "convert_queue" awaiting to be converted to a wav file
    def add_from_url(self, url):
        self.youtube_downloader.add_from_url_in_queue(url)
        self.youtube_downloader.download()

    #works like the method above but accepts a generic search term
    def add_from_title(self, title):
        self.youtube_downloader.add_from_title_in_queue(title)
        download_thread = threading.Thread(target=self.youtube_downloader.download(), name="Downloader", args=())
        download_thread.start()
        
    def separate(self,index,wait=False):
        wav_path = 'wav_files\\'+self.youtube_downloader.downloaded_file_names[index]+'.wav'
        output_path = 'separated_files'
        file_separator.convert_file(wav_path,output_path,self.youtube_downloader.downloaded_file_names[index],wait)
        pass
    #removes files at index "index" of the list downloaded_files in youtube_downloader
    def remove_file(self,index):
        file_name = self.youtube_downloader.remove_downloaded_file_from_list(index)
        os.remove(self.path+"\\wav_files\\" + file_name + ".wav")

    #prints a list of all the files that are downloaded
    def print_downloaded_files(self):
        length = len(self.youtube_downloader.downloaded_file_names)
        if length == 0:
            print('no downloaded files found')
            return
        for i in range(length):
            print(str(i)+". " + self.youtube_downloader.downloaded_file_names[i])
    
    def play_file(self, index):
        file_name= self.youtube_downloader.downloaded_file_names[index]
        pygame.mixer.stop()
        s = pygame.mixer.Sound(self.path+"\\wav_files\\"+file_name+"."+"wav")
        s.play()
        self.is_playing = True
        self.is_paused = False

    def pause_playing_file(self):
        if self.is_playing:
            if not self.is_paused:
                pygame.mixer.pause()
                self.is_paused = True
            else:
                print('music already paused')
        else:
            print('there is no music to be paused')

    def resume_playing_file(self):
        if self.is_playing:
            if self.is_paused:
                pygame.mixer.unpause()
                self.is_paused = False
            else:
                print('music is playing')
        else:
            print('there is no music to be unpaused')

    def stop_playing_file(self):
        if self.is_playing:
            pygame.mixer.stop()
            self.is_playing = False
        else:
            print('there is no music to be stopped')

        

    