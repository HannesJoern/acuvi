# acuvi
the worlds smartest music visualizer

vis_sample: beschreibt wie die led leuchten müssen: array mit länge n (bei n leds) wo jeder wert die hexadezimal darstellung
          der rgb values ist. index n beschreibt die farbe von led nr.n. wenn die leds in einer 2d form sind (also zb rechteck usw.)
          dann ist der oberste linke led nr.0 und der unterste rechte nr. n

spleeter_data: daten von spleeter, genauso wie spleeter sie ausgibt in der python API. wahrscheinlich ist das auch fast das gleiche, wie wenn man die .wav Dateien einliest

## visualizer(spleeter_data):
...
## return array of / list of n vis_samples:
Diese Funktion ist unsere Schnittstelle, die sowohl von realtime spleeter als auch von file-based spleeter benutzt wird und so ausgetauscht werden kann.
Sie nimmt spleeter-daten (rohe audio daten) und gibt n vis_samples (in hexadezimal) aus.
Die funktion ist in einer Klasse, die in ihrem Konstruktor alle Parameter entgegennimmt.




alte beschreibung:

spleeter_data: (einen dictionary mit 4 einträge:(voice,drums,bass,other) diese einträge sind listen die an stelle n den n-ten sample beinhalten
               in der form (right_sample,left_sample). Zusätzlich soll als information die samplerate gegeben werden. Bei dem hinzufügen neuer samples,
               werden einfach die neuen daten am ende der listen im dictionary hinzugefügt damit man an n-ter stelle den n-ten sample in der liste hat.
               Dieses vorgehen hat aber einen Problem, wen wir den n_ten sample an der n_ten stelle haben möchten dann wird die liste immer länger bis wir keinen
               speicher mehr haben, deshalb müssen wir nach dem benutzen der ersen x samples zur visualisierung sie von den listen entfernen und die anzahl der
               vom start des programms entfernten samples in einer variable speichern.)

so funktioniert das ganze:
  
               real time separation (1.writes in variable the sample rate of its output -> 2.starts separation -> 3.gets audio data for with a legth of 10 seconds
               -> 4.separates it-> 5.writes the data into the dictionary -> go to step 3)
               
               creation of data for visulization (gets chunks of the data that is separated -> deletes the data from the source -> elaborates the data 
               -> output looks like what is described in vis_data)
               
               the data for visualization is in the end used to vizualise the sound on whatever media is choosen by the user, be it a window on the computer, led lights,
               etc.
