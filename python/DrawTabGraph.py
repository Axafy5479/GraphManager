import io
import os
from Figure import Figure
from TabView import TabView
import sys
import pathlib


path = sys.argv[1]
tabView = TabView.load(path)
htmls = tabView.to_htmls()

tempPath = pathlib.Path(sys.argv[2],"temp\\"+sys.argv[3])
tempPath.mkdir(parents=True, exist_ok=True)
for i in range(len(htmls)):
    html = htmls[i]
    path = pathlib.Path(tempPath, "temp"+str(i)+"___tab-"+tabView._tabNames[i]+".html")
    path.write_text(html, encoding="UTF-8")
