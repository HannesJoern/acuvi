import pafy
from youtubesearchpython import VideosSearch
import os
from os import listdir
from os.path import isfile, join

#youtube_dl package has to be installed for this to work
class youtube_downloader:
    def __init__(self,path) -> None:
        self.path = path
        self.downloaded_file_names = []
        self.url_list = []
        path_ = self.path+'\\downloaded_files'
        onlyfiles = [f for f in listdir(path_) if isfile(join(path_, f))]
        onlyfiles.remove('downloaded_files_readme.txt')
        for i in onlyfiles:
            filename, file_extension = os.path.splitext(i)
            self.downloaded_file_names.append([filename,file_extension[1:]])



    #adds url to download to the url_list
    def add_url(self,url):
        self.url_list.append(url)
    
    #downloads the first link in the url_list, saves it in the folder "downloaded_files" in the same directory and returns a list of 2 with the name
    #at index 0 and the extension type at index 1
    def download(self):
        url = self.url_list.pop(0)
        stream_url = pafy.new(url)
        stream = stream_url.getbestaudio()
        extension = stream.extension
        name = self.get_name(url)
        stream.download(filepath=self.path+"\\downloaded_files\\" + name + "." + extension)
        self.downloaded_file_names.append([name,extension])
        return [name,extension]

    #this method returns the first video that pops up on youtube if search_term is put in teh serach bar
    def get_url(self,search_term):
        return VideosSearch(search_term, limit = 1).result()['result'][0]['link']
    
    #returns the neame of the video for a given url
    def get_name(self,url):
        return VideosSearch(url, limit = 1).result()['result'][0]['title'].replace(" ","_")
    
    #the input is the url of a video, if it was already downloaded this method does nothing, if not it is added to the url_list
    def add_from_url_in_queue(self, url):
        name = self.get_name(url)
        for i in self.downloaded_file_names:
            if i[0] == name:
                return 'already downloaded'
        self.add_url(url)
        return 'added to download queue'

    #same as the method before but works with a generic search term too
    def add_from_title_in_queue(self, title):
        name = self.get_name(title)
        for i in self.downloaded_file_names:
            if i[0] == name:
                return 'already_conatined'
        url = self.get_url(title)
        self.add_from_url_in_queue(url)
        return 'added to download queue'

    def remove_downloaded_file_from_list(self, index):
        return self.downloaded_file_names.pop(index)
