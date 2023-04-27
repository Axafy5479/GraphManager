import json as json2
import pathlib
import numpy as np
import plotly.graph_objects
import plotly.graph_objects as go
from plotly.io import read_json, from_json
from plotly.subplots import make_subplots
import subprocess
import uuid
import asyncio
import shutil
from collections import UserList

class Figure:

    _fontsize: int
    _font: str
    _textColor: str
    _bgColor: str
    _darkMode: bool
    _xlabel: str = None
    _ylabel: str = None
    _ylabel2: str = None
    _legendItem = []
    colorMap = {'virginica': 'rgb(255,0,0)', 'setosa': 'rgb(0,255,0)', 'versicolor': 'rgb(0,0,255)'}
    _fig: plotly.graph_objects.Figure
    _proc: subprocess.Popen = None
    _state: str
    _tempFigJson: str = ""
    _haveAnnotation: bool = False
    _uuid: str = ""
    _windowOpened: bool = False
    _inTab: bool = False


    def __init__(self, jsonDict = None, autoShow: bool = False):
        if jsonDict == None:
            self._fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])
            self._fontsize = 16
            self._font = "Times New Roman, Noto Sans CJK JP"
            self.darkMode(False, autoShow=autoShow)
            self._initialize()
            self.plot = self._instance_plot
            self.fontsize=12
            if autoShow:
                self.show()

        else:
            self.__dict__ = jsonDict
            self.plot = self._instance_plot


    def darkMode(self, isDark: bool = True, autoShow: bool = False):
        self._darkMode = isDark
        self._textColor = "white" if isDark else "black"
        self._bgColor = "black" if isDark else "white"
        self._initialize()
        if autoShow:
            self.show()
        return self

    def fontSize(self, size: int):
        self._fontsize = size
        self._fig.update_layout({
            "font": dict(
                size=self._fontsize,
            )})
        self.show()
        return self
        


    def resize(self, x: int, y: int):
        print("resizeは実装されていません")

    def _instance_plot(self, data1, data2=[], color: str = None, line: str = "", marker="", width: float = 2, size: float = 3, secondary_y: bool = False,  autoShow: bool = False):
        mode = "lines"

        if secondary_y:
            self.show2y()

        x = np.array(range(0, len(data1))) if len(data2)==0 else data1
        y = data1 if len(data2)==0 else data2

        if marker == "" and line == "":
            line = "-"

        if line == "":
            mode = "markers"
        elif marker == "":
            mode = "lines"
        else:
            mode = "lines+markers"

        dash: str = None

        if line == ".":
            dash = "dot"
        elif line == "--":
            dash = "dash"
        elif line == ".-" or line == "-.":
            dash = "dashdot"

        symbol: str = None
        if marker == ".":
            symbol = None
        elif marker == "^":
            symbol = "triangle-up"
        elif marker == "o":
            symbol = "circle-open"
        elif marker == ".":
            symbol = "circle"
        elif marker == "x":
            symbol = "x"



        self._fig.add_trace(
            go.Scatter(x=x,
                       y=y,
                       line=dict(
                           color=color,
                           dash=dash,
                           width=width),

                       marker=dict(size=size,
                                   symbol=symbol,
                                   color=color,
                                   line=dict(width=0,
                                             color='DarkSlateGrey')),

                       mode=mode),
            row=1,
            col=1,
            secondary_y=secondary_y
        )
        self._updateTick()
        if autoShow:
            self.show()
        return self


    def add_footer(self, path:str):

        if not self._haveAnnotation:
            self._haveAnnotation = True
            self._fig.add_annotation(
                dict(x=1, y=-0.3, text=path,
                                 xref='paper', yref='paper', showarrow=False,
                                 xanchor='right', yanchor='auto', xshift=0, yshift=0,
                                 font=dict(
                                     size=10,
                                     color="gray",
                                     family="Noto Sans CJK JP"
                                 ))
            )
        else:
            self._fig.update_annotations(
                dict(x=1, y=-0.3, text=path,
                                 xref='paper', yref='paper', showarrow=False,
                                 xanchor='right', yanchor='auto', xshift=0, yshift=0,
                                 font=dict(
                                     size=10,
                                     color="gray",
                                     family = "Noto Sans CJK JP"
                                 ))
            )



    @staticmethod
    def plot(data1, data2=[], color: str = None, line: str = "", marker="", width: float = 3, size: float = 3, secondary_y: bool = False, autoShow: bool = False):
        f = Figure(autoShow=False)
        f.plot(data1, data2, color, line, marker, width, size, secondary_y, autoShow)
        return f

    def plot2(self, data1, data2=[], color: str = None, line: str = "", marker="", width: float = 3, size: float = 3, autoShow: bool = False):
        self.plot(data1, data2, color, line, marker, width, size, True, autoShow)
        return self
    
    def plots(self, data1, data2: list[np.ndarray]=[], color: str = None, line: str = "", marker="", width: float = 3, size: float = 3, secondary_y: bool = False, autoShow: bool = False):
        if len(data2)>0:
            for s in data2:
                self.plot(data1, s)

        else:
            for s in data1:
                self.plot(s)
        return self


    def xlabel(self, label: str, unit: str = "", autoShow: bool = False):
        result = label if unit == "" else label + " (" + unit + ")"
        self._xlabel = result
        self._fig.update_xaxes(title=result)
        if autoShow:
            self.show()
        return self

    def ylabel(self, label: str, unit: str = "", secondary_y: bool = False, autoShow: bool = False):
        result = label if unit == "" else label+" ("+unit+")"

        if secondary_y:
            self._ylabel2 = result
        else:
            self._ylabel = result

        if secondary_y:
            self._fig.update_layout(yaxis2=dict(title=result))
        else:
            self._fig.update_yaxes(title=result)
        if autoShow:
            self.show()
        return self

    def ylabel2(self, label: str, unit: str = "", autoShow: bool = False):
        self.ylabel(label, unit, True, autoShow)
        return self

    def title(self, title: str, autoShow: bool = False):
        self._fig.update_layout(title=title)
        if autoShow:
            self.show()
        return self

    def xlim(self, l: float, r: float, autoShow: bool = False):
        self._fig.update_layout(xaxis_range=[l, r])
        if autoShow:
            self.show()
        return self

    def ylim(self, b: float, t: float, secondary_y: bool = False, autoShow: bool = False):
        if secondary_y:
            self._fig.update_layout(yaxis2=dict(range=[b, t]))
        else:
            self._fig.update_layout(yaxis_range=[b, t])
        if autoShow:
            self.show()
        return self

    def ylim2(self, b: float, t: float, autoShow: bool = False):
        self.ylim(b, t, True, autoShow)
        return self

    def show2y(self, show: bool = True):
        self._fig.update_yaxes(secondary_y=True)
        self._fig.update_layout(xaxis=dict(ticks='inside'))
        self._fig.update_layout(xaxis2=dict(ticks='inside'))
        return self


    def _initialize(self):
        self._fig.update_layout({
            "font": dict(
                family=self._font,
                size=self._fontsize,
                color=self._textColor
            ),
            "plot_bgcolor": self._bgColor,
            "paper_bgcolor": self._bgColor,
            'xaxis': {
                'showgrid': False,  # thin lines in the background
                'zeroline': False,  # thick line at x=0
                "ticks": 'inside',
                "tickformat": ",",
                "showline": True,
                "linecolor": self._textColor,
                "mirror": 'allticks',
                "tickcolor": self._textColor,
            },  # the same for yaxis
            'xaxis2': {
                'showgrid': False,  # thin lines in the background
                'zeroline': False,  # thick line at x=0
                "ticks": 'inside',
                "showline": True,
                "linecolor": self._textColor,
                "tickformat": ",",
                "mirror": 'allticks',
                "tickcolor": self._textColor
            },  # the same for yaxis
            'yaxis': {
                'showgrid': False,  # thin lines in the background
                'zeroline': False,  # thick line at x=0
                "ticks": 'inside',
                "tickformat": ",",
                "showline": True,
                "linecolor": self._textColor,
                "mirror": 'allticks',
                "tickcolor": self._textColor,
            },  # the same for yaxis
            'yaxis2': {
                'showgrid': False,  # thin lines in the background
                'zeroline': False,  # thick line at x=0
                "ticks": 'inside',
                "showline": True,
                "tickformat": ",",
                "linecolor": self._textColor,
                "mirror": 'allticks',
                "tickcolor": self._textColor,
            },  # the same for yaxis
        })
        self._fig.update_layout(xaxis=dict(ticks='inside'))
        self._fig.update_layout(xaxis2=dict(ticks='inside'))
        self._updateTick()

    def _updateTick(self):
        exist_y2 = False
        for d in self._fig.data:
            if d["yaxis"] == "y2":
                exist_y2 = True
                break
        
        self._fig.update_layout({
            "yaxis": {
                "mirror": True if exist_y2 else "allticks"
            },
            "yaxis2": {
                "mirror": True if exist_y2 else "allticks"
            }
        })


    def fontsize(self, size: int):
        self._fontsize = size
        self._initialize()
        self.show()
        return self

    def legend(self, legendNames, autoShow: bool = False):
        for i in range(0, len(legendNames)):
            if i < len(self._fig['data']):
                self._fig['data'][i]['showlegend'] = True
                self._fig['data'][i]['name'] = legendNames[i]
            else:
                print(str(i)+"はlegendの個数がデータ数を超えています")
                break
        if autoShow:
            self.show()
        return self

    def show(self):
        if self._inTab:
            return
        # self.close()
        if not self._windowOpened:
            self._uuid = str(uuid.uuid4())
        elif self._uuid == "":
            print("通信に使用するidが存在しません。新しくグラフを生成します")
            self._uuid = str(uuid.uuid4())
        else:
            tempDir = pathlib.Path(pathlib.Path(__file__).parent.parent, "temp\\"+self._uuid)
            if tempDir.exists:
                shutil.rmtree(tempDir)

        html = self._fig.to_html()
        path = pathlib.Path(pathlib.Path(__file__).parent.parent, "temp\\"+self._uuid+"\\temp.html")
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(html, encoding="UTF-8")

        if self._windowOpened:
            pathlib.Path(path.parent,".star").touch()
        else:
            exePath = pathlib.Path(path.parent.parent.parent, r"GraphDrawer.exe")

            self._proc = subprocess.Popen([str(exePath), "showHTML", self._uuid])
            asyncio.get_event_loop().run_in_executor(None, self.communicating)
        return self

    def communicating(self):
        self._windowOpened = True
        if self._proc == None:
            self._windowOpened = False
            return
        self._proc.communicate()
        self._windowOpened = False


    def close(self):
        if self._proc != None:
            self._proc.kill()
            self._proc = ""

    # def serialize(self):
    #     return str(self._fig.to_json())

    def getDict(self):
        return self._fig.to_dict()


    @staticmethod
    def load(path: str):
        f = open(path, 'r')
        j = f.read()
        fig = Figure.deserialize(j)
        fig._inTab = False
        return fig

    def save(self, p: str):
        p += ".sun"
        path = pathlib.Path(p)
        if not path.is_absolute():
            path = path.absolute()

        path.parent.mkdir(exist_ok=True, parents=True)
        self.add_footer(str(path))

        path.write_text(self.serialize())

    def serialize(self):
        temp = self._fig
        temp_plot = self.plot
        temp_proc = self._proc
        temp_win_opened = self._windowOpened
        self._tempFigJson = self._fig.to_json()
        self._fig = None
        self._proc=None
        self.plot = None
        self._windowOpened = False

        result = json2.dumps(self.__dict__)
        # result = json2.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

        self._fig = temp
        self.plot = temp_plot
        self._proc = temp_proc
        self._windowOpened = temp_win_opened
        return result

    @staticmethod
    def deserialize(jsonString:str):
        jsonDict = json2.loads(jsonString)
        fig: Figure = Figure(jsonDict)
        fig._fig = from_json(fig._tempFigJson)
        fig._tempFigJson = ""
        return fig

    def to_html(self):
        return self._fig.to_html()

    def getData(self):
        ans = []
        for d in self._fig.data:
            abData = []
            ans.append([np.array(d["x"]),np.array(d["y"])])

        return ans

class TabView(UserList):

    _figs: list[Figure]
    _tabNames: list[str]

    _figJsonStrings: list[str]
    _proc: subprocess.Popen = None

    _windowOpened: bool = False

    def __init__(self, figs: list[Figure], tabNames: list[str], deserializedDict = []):

        if len(deserializedDict) == 0:
            if(len(figs)!=len(tabNames)):
                print("図の数とタブ数が一致しません")
            self._figs = figs
            for fig in self._figs:
                fig._inTab = True
            self._tabNames = tabNames
            self._figJsonStrings = []
            super().__init__(self._figs)
            self.show()

        else:
            self.__dict__ = deserializedDict
        
        

    def insert(self, i: int, item: Figure) -> None:
        self._figs.insert(i, item)
        self._tabNames.insert(i, item)
        super().insert(i, item)
        for fig in self._figs:
                fig._inTab = True
        self.show()



    def extend(self, items: list[Figure]) -> None:
        self._figs.insert(items)
        for fig in self._figs:
                fig._inTab = True
        self._tabNames.insert(items)
        super().extend(items)
        self.show()

    def __delitem__(self, i: int) -> Figure:
        fig = self._figs[i]
        fig._inTab = False
        self.removeAt(i)
        return super().__delitem__(i)
        self.show()
        return fig


    def show(self):

        if not self._windowOpened:
            self._uuid = str(uuid.uuid4())
        elif self._uuid == "":
            print("通信に使用するidが存在しません。新しくグラフを生成します")
            self._uuid = str(uuid.uuid4())
        else:
            tempDir = pathlib.Path(pathlib.Path(__file__).parent.parent, "temp\\"+self._uuid)
            if tempDir.exists:
                shutil.rmtree(tempDir)

        tempFolder = pathlib.Path(pathlib.Path(__file__).parent.parent, "temp\\"+self._uuid)
        tempFolder.mkdir(exist_ok=True, parents=True)
        for i in range(len(self._figs)):
            pathlib.Path(tempFolder, "temp" + str(i) + "___tab-"+self._tabNames[i]+".html").write_text(self._figs[i].to_html(), encoding='UTF-8')

        if self._windowOpened:
            pathlib.Path(tempFolder,".star").touch()
        else:
            p = pathlib.Path(tempFolder.parent.parent, r"GraphDrawer.exe")
            args: list[str] = [str(p), "showTabView",self._uuid, str(len(self._figs))]
            for tabName in self._tabNames:
                args.append(tabName)

            self._proc = subprocess.Popen(args)
            asyncio.get_event_loop().run_in_executor(None, self.communicating)

    def communicating(self):
        self._windowOpened = True
        if self._proc == None:
            self._windowOpened = False
            return
        self._proc.communicate()
        self._windowOpened = False

    
    def close(self):
        if(self._proc != None):
            self._proc.kill()

    def save(self, p:str):
        p += ".sunny"
        path = pathlib.Path(p)
        if not path.is_absolute():
            path = path.absolute()

        for fig in self._figs:
            fig.add_footer(str(path))
            self._figJsonStrings.append(fig.serialize())

        f = open(str(path), 'w')
        f.write(self.serialize())
        f.close()

    def serialize(self)->str:
        self._figJsonStrings.clear()
        for f in self._figs:
            self._figJsonStrings.append(f.serialize())
        figs = self._figs
        self._figs = []
        super().clear()
        proc = self._proc
        self._proc = None

        result = json2.dumps(self.__dict__)

        self._figs = figs
        self._proc = proc
        super().__init__(figs)
        
        return result

    def to_htmls(self)->list[str]:
        htmls:list[str] = []
        for fig in self._figs:
            htmls.append(fig.to_html())
        return htmls

    def append(self, fig:Figure, tabName:str):
        self._figs.append(fig)
        for fig in self._figs:
                fig._inTab = True
        self._tabNames.append(tabName)
        super().append(fig)
        self.show()
    
    def _append_for_deserialization(self, fig:Figure):
        fig._inTab = True
        self._figs.append(fig)
        super().append(fig)


        
    def removeAt(self, index:int)->Figure:
        fig = self._figs[index]   
        fig._inTab = False
        del self._figs[index]
        del self._tabNames[index]
        self.show()
        return fig

    @staticmethod
    def load(path):
        f = open(path, 'r')
        j = f.read()
        return TabView.deserialize(j)

    @staticmethod
    def deserialize(jsonString:str):
        deserializedDict = json2.loads(jsonString)
        tabView: TabView = TabView(figs=[], tabNames=[], deserializedDict=deserializedDict)
        for fig in tabView._figJsonStrings:
            tabView._append_for_deserialization(Figure.deserialize(fig))
        tabView._figJsonStrings = []
        tabView._windowOpened = False
        return tabView

def figure():
    return Figure(autoShow=False)

def plot(data1, data2=[], color: str = None, line: str = "", marker="", width: float = 3, size: float = 3, secondary_y: bool = False, autoShow: bool = False):
    f = Figure(autoShow=False)
    f.plot(data1, data2, color, line, marker, width, size, secondary_y, autoShow)
    return f

def plots(data1, data2: list[np.ndarray]=[], color: str = None, line: str = "", marker="", width: float = 3, size: float = 3, secondary_y: bool = False, autoShow: bool = False):
    f = Figure(autoShow=False)
    f.plots(data1, data2, color, line, marker, width, size, secondary_y, autoShow)
    return f

def tabView(figs: list[Figure], tabNames: list[str], deserializedDict = []):
    return TabView(figs, tabNames, deserializedDict)
