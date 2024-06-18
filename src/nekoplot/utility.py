import numpy as np

def histogram_proc(hist):
    # ヒストグラムの変化のない中間値をトリムする
    h = hist[1]>0
    hm = np.append(h[1:],True)
    hp = np.append(True,h[:-1])
    dil = np.any(np.array([h,hm,hp]),axis=0)
    return hist[:,dil].T
