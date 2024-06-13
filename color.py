
import numpy as np
from cv2 import (cvtColor,applyColorMap,COLOR_BGR2RGBA,COLORMAP_AUTUMN,COLORMAP_BONE,COLORMAP_JET,COLORMAP_WINTER
                ,COLORMAP_RAINBOW,COLORMAP_OCEAN,COLORMAP_SUMMER,COLORMAP_SPRING
                ,COLORMAP_COOL,COLORMAP_HSV,COLORMAP_PINK,COLORMAP_HOT,COLORMAP_PARULA,COLORMAP_MAGMA
                ,COLORMAP_INFERNO,COLORMAP_PLASMA,COLORMAP_VIRIDIS,COLORMAP_CIVIDIS
                ,COLORMAP_TWILIGHT,COLORMAP_TWILIGHT_SHIFTED,COLORMAP_DEEPGREEN)

import skia

def gray_to_rgb(x,cmap):
    im = cvtColor(applyColorMap((x).astype(np.uint8),cmap),COLOR_BGR2RGBA)
    return im
cv_cm = [COLORMAP_AUTUMN,COLORMAP_BONE,COLORMAP_JET,COLORMAP_WINTER
        ,COLORMAP_RAINBOW,COLORMAP_OCEAN,COLORMAP_SUMMER,COLORMAP_SPRING
        ,COLORMAP_COOL,COLORMAP_HSV,COLORMAP_PINK,COLORMAP_HOT,COLORMAP_PARULA,COLORMAP_MAGMA
        ,COLORMAP_INFERNO,COLORMAP_PLASMA,COLORMAP_VIRIDIS,COLORMAP_CIVIDIS
        ,COLORMAP_TWILIGHT,COLORMAP_TWILIGHT_SHIFTED,COLORMAP_DEEPGREEN]
global cm
cm = dict(
        autumn = COLORMAP_AUTUMN,
        bone = COLORMAP_BONE,
        jet = COLORMAP_JET,
        winter = COLORMAP_WINTER,
        rainbow = COLORMAP_RAINBOW,
        ocean = COLORMAP_OCEAN,
        summer = COLORMAP_SUMMER,
        spring = COLORMAP_SPRING,
        cool = COLORMAP_COOL,
        hsv = COLORMAP_HSV,
        pink = COLORMAP_PINK,
        hot = COLORMAP_HOT,
        parula = COLORMAP_PARULA,
        magma = COLORMAP_MAGMA,
        inferno = COLORMAP_INFERNO,
        plasma = COLORMAP_PLASMA,
        viridis = COLORMAP_VIRIDIS,
        cividis = COLORMAP_CIVIDIS,
        twilight = COLORMAP_TWILIGHT,
        s_twilight = COLORMAP_TWILIGHT_SHIFTED,
        deepgreen = COLORMAP_DEEPGREEN,
        )

def append_ColorMap(key,colormap):
    global cm
    cm[key] = colormap

class Color:
    def __init__(self,r=0.,g=0.,b=0.,a=1.0):
        if not((0<=r<=1) and (0<=g<=1) and (0<=b<=1) and (0<=a<=1)):
            raise RuntimeError("Color(red:float, green:float, blue:float, alpha:float) r,g,b,a in [0,1]")
        self.red = r
        self.green = g
        self.blue = b
        self.alpha = a

    def fromU8(r=0,g=0,b=0,a=255):
        if not((0<=r<=255) and (0<=g<=255) and (0<=b<=255) and (0<=a<=255)):
            raise RuntimeError("Color(red:int, green:int, blue:int, alpha:int) r,g,b,a in [0,255]")
        return Color(r/255.,g/255.,b/255.,a/255.)

    def __str__(self):
        return self.colorcode

    def __repr__(self):
        return self.colorcode

    @property
    def i4(self):
        return (int(255*self.red),int(255*self.green),int(255*self.blue),int(255*self.alpha))

    @property
    def i3(self):
        return (int(255*self.red),int(255*self.green),int(255*self.blue))

    @property
    def i32(self):
        return np.uint32(((int(255*self.red)&0xFF))+((int(255*self.green)&0xFF)<<8)+((int(255*self.blue)&0xFF)<<16)+((int(255*self.alpha)&0xFF)<<24))

    @property
    def f(self):
        return (self.red,self.green,self.blue,self.alpha)

    @property
    def f3(self):
        return (self.red,self.green,self.blue)

    @property
    def skia4f(self):
        return skia.Color4f(*self.f)

    @property
    def colorcode(self):
        return f"#{int(255*self.red):0>2X}{int(255*self.green):0>2X}{int(255*self.blue):0>2X}{int(255*self.alpha):0>2X}"
    @property
    def colorcode3(self):
        return f"#{int(255*self.red):0>2X}{int(255*self.green):0>2X}{int(255*self.blue):0>2X}"

    @colorcode.setter
    def colorcode(self,value):
        if value.startswith("#"):
            self.red = int(value[1:3],base=16)/255.
            self.green = int(value[3:5],base=16)/255.
            self.blue = int(value[5:7],base=16)/255.
            self.alpha = int(value[7:9],base=16)/255.
    @colorcode3.setter
    def colorcode3(self,value):
        if value.startswith("#"):
            self.red = int(value[1:3],base=16)/255.
            self.green = int(value[3:5],base=16)/255.
            self.blue = int(value[5:7],base=16)/255.
            self.alpha = 1.0

ColorList = {
    'c-blue': Color.fromU8(31, 119, 180),
    'c-orange': Color.fromU8(255, 127, 14),
    'c-green': Color.fromU8(44, 160, 44),
    'c-red': Color.fromU8(214, 39, 40),
    'c-purple': Color.fromU8(148, 103, 189),
    'c-brown': Color.fromU8(140, 86, 75),
    'c-pink': Color.fromU8(227, 119, 194),
    'c-gray': Color.fromU8(127, 127, 127),
    'c-olive': Color.fromU8(188, 189, 34),
    'c-cyan': Color.fromU8(23, 190, 207),
    "white" : Color.fromU8(255,255,255),
    "whitesmoke" : Color.fromU8(245,245,245),
    "ghostwhite" : Color.fromU8(248,248,255),
    "aliceblue" : Color.fromU8(240,248,255),
    "lavender" : Color.fromU8(230,230,250),
    "azure" : Color.fromU8(240,255,255),
    "lightcyan" : Color.fromU8(224,255,255),
    "mintcream" : Color.fromU8(245,255,250),
    "honeydew" : Color.fromU8(240,255,240),
    "ivory" : Color.fromU8(255,255,240),
    "beige" : Color.fromU8(245,245,220),
    "lightyellow" : Color.fromU8(255,255,224),
    "lightgoldenrodyellow" : Color.fromU8(250,250,210),
    "lemonchiffon" : Color.fromU8(255,250,205),
    "floralwhite" : Color.fromU8(255,250,240),
    "oldlace" : Color.fromU8(253,245,230),
    "cornsilk" : Color.fromU8(255,248,220),
    "papayawhite" : Color.fromU8(255,239,213),
    "blanchedalmond" : Color.fromU8(255,235,205),
    "bisque" : Color.fromU8(255,228,196),
    "snow" : Color.fromU8(255,250,250),
    "linen" : Color.fromU8(250,240,230),
    "antiquewhite" : Color.fromU8(250,235,215),
    "seashell" : Color.fromU8(255,245,238),
    "lavenderblush" : Color.fromU8(255,240,245),
    "mistyrose" : Color.fromU8(255,228,225),
    "gainsboro" : Color.fromU8(220,220,220),
    "lightgray" : Color.fromU8(211,211,211),
    "lightsteelblue" : Color.fromU8(176,196,222),
    "lightblue" : Color.fromU8(173,216,230),
    "lightskyblue" : Color.fromU8(135,206,250),
    "powderblue" : Color.fromU8(176,224,230),
    "paleturquoise" : Color.fromU8(175,238,238),
    "skyblue" : Color.fromU8(135,206,235),
    "mediumaquamarine" : Color.fromU8(102,205,170),
    "aquamarine" : Color.fromU8(127,255,212),
    "palegreen" : Color.fromU8(152,251,152),
    "lightgreen" : Color.fromU8(144,238,144),
    "khaki" : Color.fromU8(240,230,140),
    "palegoldenrod" : Color.fromU8(238,232,170),
    "moccasin" : Color.fromU8(255,228,181),
    "navajowhite" : Color.fromU8(255,222,173),
    "peachpuff" : Color.fromU8(255,218,185),
    "wheat" : Color.fromU8(245,222,179),
    "pink" : Color.fromU8(255,192,203),
    "lightpink" : Color.fromU8(255,182,193),
    "thistle" : Color.fromU8(216,191,216),
    "plum" : Color.fromU8(221,160,221),
    "silver" : Color.fromU8(192,192,192),
    "darkgray" : Color.fromU8(169,169,169),
    "lightslategray" : Color.fromU8(119,136,153),
    "slategray" : Color.fromU8(112,128,144),
    "slateblue" : Color.fromU8(106,90,205),
    "steelblue" : Color.fromU8(70,130,180),
    "mediumslateblue" : Color.fromU8(123,104,238),
    "royalblue" : Color.fromU8(65,105,225),
    "blue" : Color.fromU8(0,0,255),
    "dodgerblue" : Color.fromU8(30,144,255),
    "cornflowerblue" : Color.fromU8(100,149,237),
    "deepskyblue" : Color.fromU8(0,191,255),
    "cyan" : Color.fromU8(0,255,255),
    "aqua" : Color.fromU8(0,255,255),
    "turquoise" : Color.fromU8(64,224,208),
    "mediumturquoise" : Color.fromU8(72,209,204),
    "darkturquoise" : Color.fromU8(0,206,209),
    "lightseagreen" : Color.fromU8(32,178,170),
    "mediumspringgreen" : Color.fromU8(0,250,154),
    "springgreen" : Color.fromU8(0,255,127),
    "lime" : Color.fromU8(0,255,0),
    "limegreen" : Color.fromU8(50,205,50),
    "yellowgreen" : Color.fromU8(154,205,50),
    "lawngreen" : Color.fromU8(124,252,0),
    "chartreuse" : Color.fromU8(127,255,0),
    "greenyellow" : Color.fromU8(173,255,47),
    "yellow" : Color.fromU8(255,255,0),
    "gold" : Color.fromU8(255,215,0),
    "orange" : Color.fromU8(255,165,0),
    "darkorange" : Color.fromU8(255,140,0),
    "goldenrod" : Color.fromU8(218,165,32),
    "burlywood" : Color.fromU8(222,184,135),
    "tan" : Color.fromU8(210,180,140),
    "sandybrown" : Color.fromU8(244,164,96),
    "darksalmon" : Color.fromU8(233,150,122),
    "lightcoral" : Color.fromU8(240,128,128),
    "salmon" : Color.fromU8(250,128,114),
    "lightsalmon" : Color.fromU8(255,160,122),
    "coral" : Color.fromU8(255,127,80),
    "tomato" : Color.fromU8(255,99,71),
    "orangered" : Color.fromU8(255,69,0),
    "red" : Color.fromU8(255,0,0),
    "deeppink" : Color.fromU8(255,20,147),
    "hotpink" : Color.fromU8(255,105,180),
    "palevioletred" : Color.fromU8(219,112,147),
    "violet" : Color.fromU8(238,130,238),
    "orchid" : Color.fromU8(218,112,214),
    "magenta" : Color.fromU8(255,0,255),
    "fuchsia" : Color.fromU8(255,0,255),
    "mediumorchid" : Color.fromU8(186,85,211),
    "darkorchid" : Color.fromU8(153,50,204),
    "darkviolet" : Color.fromU8(148,0,211),
    "blueviolet" : Color.fromU8(138,43,226),
    "mediumpurple" : Color.fromU8(147,112,219),
    "gray" : Color.fromU8(128,128,128),
    "mediumblue" : Color.fromU8(0,0,205),
    "darkcyan" : Color.fromU8(0,139,139),
    "cadetblue" : Color.fromU8(95,158,160),
    "darkseagreen" : Color.fromU8(143,188,143),
    "mediumseagreen" : Color.fromU8(60,179,113),
    "teal" : Color.fromU8(0,128,128),
    "forestgreen" : Color.fromU8(34,139,34),
    "seagreen" : Color.fromU8(46,139,87),
    "darkkhaki" : Color.fromU8(189,183,107),
    "peru" : Color.fromU8(205,133,63),
    "crimson" : Color.fromU8(220,20,60),
    "indianred" : Color.fromU8(205,92,92),
    "rosybrown" : Color.fromU8(188,143,143),
    "mediumvioletred" : Color.fromU8(199,21,133),
    "dimgray" : Color.fromU8(105,105,105),
    "black" : Color.fromU8(0,0,0),
    "midnightblue" : Color.fromU8(25,25,112),
    "darkslateblue" : Color.fromU8(72,61,139),
    "darkblue" : Color.fromU8(0,0,139),
    "navy" : Color.fromU8(0,0,128),
    "darkslategray" : Color.fromU8(47,79,79),
    "green" : Color.fromU8(0,128,0),
    "darkgreen" : Color.fromU8(0,100,0),
    "darkolivegreen" : Color.fromU8(85,107,47),
    "olivedrab" : Color.fromU8(107,142,35),
    "olive" : Color.fromU8(128,128,0),
    "darkgoldenrod" : Color.fromU8(184,134,11),
    "chocolate" : Color.fromU8(210,105,30),
    "sienna" : Color.fromU8(160,82,45),
    "saddlebrown" : Color.fromU8(139,69,19),
    "firebrick" : Color.fromU8(178,34,34),
    "brown" : Color.fromU8(165,42,42),
    "maroon" : Color.fromU8(128,0,0),
    "darkred" : Color.fromU8(139,0,0),
    "darkmagenta" : Color.fromU8(139,0,139),
    "purple" : Color.fromU8(128,0,128),
    "indigo" : Color.fromU8(75,0,130),
}

class ColorMap:
    def __init__(self,*args):
        self._cm = None
        if len(args)==1:
            if isinstance(args[0],int):
                if args[0] in cv_cm:
                    self._cm = args[0]
                    self.red,self.green,self.blue,self.alpha = cvtColor(applyColorMap(np.arange(256,dtype=np.uint8).reshape(256,1,1),self._cm),COLOR_BGR2RGBA).T
            if isinstance(args[0],str):
                if args[0] in cm:
                    self._cm = cm[args[0]]
                    self.red,self.green,self.blue,self.alpha = cvtColor(applyColorMap(np.arange(256,dtype=np.uint8).reshape(256,1,1),self._cm),COLOR_BGR2RGBA).T
            elif isinstance(args[0],np.ndarray):
                if args[0].ndim == 3 and args[0].shape[2] == 3:
                    red,green,blue = args[0].reshape(args[0].shape[0],3).T
                    alpha = np.ones_like(red)*255
                    xs = np.linspace(0,1,len(red),True)
                    self._cm = args[0].copy()
            else:
                # List[Color] 想定
                arr = ColorMap._Make_Linear(args[0])
                red,green,blue = arr.reshape(arr.shape[0],3).T
                alpha = np.ones_like(red)*255
                xs = np.linspace(0,1,len(red),True)
                self._cm = arr.copy()
        elif len(args) == 2:
            arr = ColorMap._Make_Linear(args[0],args[1])
            red,green,blue = arr.reshape(arr.shape[0],3).T
            alpha = np.ones_like(red)*255
            xs = np.linspace(0,1,len(red),True)
            self._cm = arr.copy()
        elif len(args) == 3:
            arr = ColorMap._Make_Linear(args[0],args[1],args[2])
            red,green,blue = arr.reshape(arr.shape[0],3).T
            alpha = np.ones_like(red)*255
            xs = np.linspace(0,1,len(red),True)
            self._cm = arr.copy()
        self.red = lambda x:np.interp(x,xs,red)
        self.green = lambda x:np.interp(x,xs,green)
        self.blue = lambda x:np.interp(x,xs,blue)
        self.alpha = lambda x:np.interp(x,xs,alpha)

    def __call__(self,xs):
        if isinstance(xs,(float,int)):
            print(self.red(xs),self.green(xs),self.blue(xs),self.alpha(xs))
            return Color.fromU8(self.red(xs),self.green(xs),self.blue(xs),self.alpha(xs))
        else:
            return np.array([Color.fromU8(r,g,b,a) for r,g,b,a in zip(self.red(xs),self.green(xs),self.blue(xs),self.alpha(xs))])

    def _Make_Linear(colors,values=None,N=256):
        if values is None:
            values = np.linspace(0,1,len(colors),True)
        rgbs = np.array([c.i3 for c in colors])
        xs = np.linspace(0,1,N,True)
        rs,gs,bs = rgbs.T
        rf = np.rint(np.interp(xs,values,rs)).astype(np.uint8)
        gf = np.rint(np.interp(xs,values,gs)).astype(np.uint8)
        bf = np.rint(np.interp(xs,values,bs)).astype(np.uint8)
        return np.reshape(np.array([bf,gf,rf],dtype=np.uint8).T,(N,1,3))

    def Make_Linear(colors,values=None,N=256):
        return ColorMap(ColorMap._Make_Linear(colors,values,N))

    def apply(self,img):
        return cvtColor(applyColorMap((img).astype(np.uint8),self._cm),COLOR_BGR2RGBA)