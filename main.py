import subprocess
import input_factory
import sys
import multiprocessing
#stream_url = pafy.new('https://www.youtube.com/watch?v=hjcB7MOop78')
#stream = stream_url.getbestaudio()
#stream.download('C:\\Users\\emhz\\Documents\\Python\\acuvi\\audio_input\\downloaded_files\\Oliver_Heldens_X_Becky_Hill_-_Gecko_Overdrive_(Stop_Thief_Remix).webm')
if __name__=='__main__':
    multiprocessing.freeze_support()
    print('\nwelcome, type help to see commands,\nthe only avalable factory type is youtube for now, type yt or youtube\n')
    val = input("select factory type from yt\stream: ")
    factory = input_factory.factory(input_type=val)

    while True:
        val = input("state your command:   ").split()
        
        if val[0] == 'download':
            if val[1] == 'url':
                factory.add_from_url(val[2])
                continue
            if val[1] == 'title':
                name = ""
                for i in range(2,len(val)):
                    name = name + val[i] + " "
                name = name[:-1]
                print('adding ' + name)
                factory.add_from_title(name)
                continue
        if val[0] == 'separate':
            factory.separate(int(val[1]))
            continue

        if val[0] == 'show':
            if val[1] == 'downloads':
                factory.print_downloaded_files()
                continue

        if val[0] == 'remove':
            factory.remove_file(int(val[1]))
            continue

        if val[0] == 'play':
            factory.play_file(int(val[1]))
            continue

        if val[0] == 'pause':
            factory.pause_playing_file()
            continue
        
        if val[0] == 'resume':
            factory.resume_playing_file()
            continue

        if val[0] == 'stop':
            factory.stop_playing_file()
            continue

        if val[0] == 'help':
            print('\ndownload + title + "name of youtube search term"  or download +  url + "url to download" to download music\nshow + downloads to show already downloadad songs\nremove + "index" to remove song at the specified index\nplay + "index" to play song at the specified index\npause,resume,stop to pause resume or stop the playing song\nkill to exit the program\n')
            continue

        if val[0] == 'kill':
            sys.exit()

        if val[0] == 'vis':
            name = factory.youtube_downloader.downloaded_file_names[int(val[1])]
            factory.separate(int(val[1]),wait=True)
            command = 'conda activate Spleeter_environment & python file_visualizer.py "{path}" "{name}"'.format(path = factory.path,name = name)
            handle = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True,encoding='utf8',cwd=factory.path, creationflags=subprocess.CREATE_NEW_CONSOLE)
            continue
        
        print('no such command, type help for command list')

