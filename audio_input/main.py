import input_factory

factory = input_factory.factory('yt')
factory.add_from_url('https://www.youtube.com/watch?v=HNtz05bhI1k')
factory.convert_to_wav()
print(factory.youtube_downloader.downloaded_file_names)
factory.remove_file(0)
print(factory.youtube_downloader.downloaded_file_names)



