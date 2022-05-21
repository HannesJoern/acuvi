def rgb_to_hex(r, g, b):
    return '0x{:02x}{:02x}{:02x}'.format(clamp(r), clamp(g), clamp(b))


#in case our data processing makes mistakes, we make sure our endpoint will take the data
def clamp(a):
    if(a<0):
        print("clamped value :" +str(a))
        return 0
    if(a>255):
        print("clamped value :" +str(a))
        return 255
    else:
        return int(a)

    
#vis_sample: 1D-array mit shape 300 und hexadezimalen RGB Werten, womit jede LED in einem sample beschrieben werden kann

#visualization: 3D-array: Sequenz aus vis_samples mit Länge FPS*CHUNKLENGTH = 30 * 10s = 300 




