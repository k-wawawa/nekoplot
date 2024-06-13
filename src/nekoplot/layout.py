
class AbstructLayout:
    def __init__(self):
        self.children = []

    def calcurate(self,width,height):
        # width,height から計算してchildrenに適用する部分
        pass

class NullLayout(AbstructLayout):
    def calcurate(self,width,height):
        pass#print(width,height)

class LayoutSize:
    def __init__(self,rel=0,abs=0):
        # 比率
        self.rel = rel
        # 絶対値
        self.abs = abs

    def __add__(self,a):
        return LayoutSize(self.rel+a.rel,self.abs+a.abs)

    def __iadd__(self,a):
        self.rel += a.rel
        self.abs += a.abs
        return self

class AbsLayout(AbstructLayout):
    pass

class GridLayout(AbstructLayout):
    class GridLayoutChild:
        def __init__(self,child,columnstart=0,rowstart=0,columnspan=1,rowspan=1):
            self.child = child
            self.columnstart = columnstart
            self.rowstart = rowstart
            self.columnspan = columnspan
            self.rowspan = rowspan

    def __init__(self,*args,**dargs):
        super().__init__(*args,**dargs)
        self.columns = list()
        self.rows = list()
        self.size = None
        self.children = list()

    def calcurate(self,width,height):
        w = LayoutSize()
        for size in self.columns:
            w += size
        r = (width-w.abs)/w.rel if w.rel>0 else 0
        col = [int(r*s.rel+s.abs) for s in [LayoutSize()]+self.columns+[LayoutSize()]]
        for i in range(len(col[1:])):
            col[i+1] += col[i]
        h = LayoutSize()
        for size in self.rows:
            h += size
        r = (height-h.abs)/h.rel if h.rel>0 else 0
        row = [int(r*s.rel+s.abs) for s in [LayoutSize()]+self.rows+[LayoutSize()]]
        for i in range(len(row[1:])):
            row[i+1] += row[i]
        self.size = (col,row)
        for child in self.children:
            l = self.size[0][child.columnstart]
            r = self.size[0][child.columnstart+child.columnspan]-1
            t = self.size[1][child.rowstart]
            b = self.size[1][child.rowstart+child.rowspan]-1
            child.child.LTRB = (l,t,r,b)

    def addColumn(self,col=None):
        col = LayoutSize(1) if col is None else col
        self.columns.append(col)

    def addRow(self,row=None):
        r = LayoutSize(1) if row is None else row
        self.rows.append(r)

    def add(self,child,columnstart=0,rowstart=0,columnspan=1,rowspan=1):
        self.children.append(GridLayout.GridLayoutChild(child,columnstart,rowstart,columnspan,rowspan))
