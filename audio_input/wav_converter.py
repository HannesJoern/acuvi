import os
import subprocess

#converts a file with the name "name" and the extension "extension_input" to a file with the same "name" and the "extension_output"
#ffmpeg has to be installed for this to work
def convert_file(name,extension_input,extensoin_output):
    command = "C:\\ffmpeg\\bin\\ffmpeg -i {video} {output}".format(video="C:\\Users\\emhz\\Documents\\Python\\acuvi\\audio_input\\downloaded_files\\" + name + "." + extension_input,
                                                  output="C:\\Users\\emhz\\Documents\\Python\\acuvi\\audio_input\\wav_files\\" + name + "." + extensoin_output)
    print(command)
    subprocess.call(command,shell=True, env={'PATH': os.getenv('PATH')})


