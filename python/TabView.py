from Figure import Figure
import json
import pathlib
import subprocess
import uuid
import asyncio
from collections import UserList
import shutil

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
            fig.add_footer(p)
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

        result = json.dumps(self.__dict__)

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
        deserializedDict = json.loads(jsonString)
        tabView: TabView = TabView(figs=[], tabNames=[], deserializedDict=deserializedDict)
        for fig in tabView._figJsonStrings:
            tabView._append_for_deserialization(Figure.deserialize(fig))
        tabView._figJsonStrings = []
        tabView._windowOpened = False
        return tabView
