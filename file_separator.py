import subprocess
import pathlib
import os
import wave
import contextlib
#converts a file with the name "name" and the extension "extension_input" to a file with the same "name" and the "extension_output"
#ffmpeg has to be installed for this to work
def convert_file(input_path,output_path,name,wait):
    current_dir = str(pathlib.Path(__file__).parent.resolve())
    
    """separator = Separator('spleeter:4stems')
    separator.separate_to_file(current_dir + "/" + input_path, current_dir + "/" + output_path)"""

    """print(current_dir + "\\" + output_path)
    print(current_dir + "\\" + input_path)
    command = 'conda activate Spleeter_environment & spleeter separate -p spleeter:4stems -o "{output}" "{input}" '.format(output = current_dir + "\\" + output_path,input = current_dir + "\\" + input_path)
    subprocess.run(command,shell=True)"""
    #print(current_dir + "\\" + output_path)
    #print(current_dir + "\\" + input_path)
    if not(os.path.isfile(current_dir+"\\"+output_path+"\\"+name+"\\vocals.wav") and os.path.isfile(current_dir+"\\"+output_path+"\\"+name+"\\bass.wav") and os.path.isfile(current_dir+"\\"+output_path+"\\"+name+"\\drums.wav") and os.path.isfile(current_dir+"\\"+output_path+"\\"+name+"\\other.wav")):
        command = 'conda activate Spleeter_environment & spleeter separate -p spleeter:4stems -o "{output}" "{input}" '.format(output = current_dir + "\\" + output_path,input = current_dir + "\\" + input_path)
        p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True,encoding='utf8')
        if wait:
            p.wait()
    
    #subprocess.run(command,shell=True)
    
    
    #p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(100)'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    


