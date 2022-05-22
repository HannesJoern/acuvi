import os
import subprocess

#converts a file with the name "name" and the extension "extension_input" to a file with the same "name" and the "extension_output"
#ffmpeg has to be installed for this to work
def convert_file(name,extension_input,extensoin_output,path):
    command = "C:\\ffmpeg\\bin\\ffmpeg -i {video} {output}".format(video=path+"\\downloaded_files\\" + name + "." + extension_input,
                                                  output=path+"\\wav_files\\" + name + "." + extensoin_output)
    print(command)
    subprocess.call(command,shell=True, env={'PATH': os.getenv('PATH')})


