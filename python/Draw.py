import io
import os
from Figure import Figure
import sys
import webbrowser
import plotly
import pathlib



path = sys.argv[1]
fig = Figure.load(path)
html = fig.to_html()

pathlib.Path(r"c:\users\sunny\temp\temp.txt").write_text(sys.argv[2])

path = pathlib.Path(sys.argv[2], 'temp\\'+sys.argv[3]+'\\temp.html')
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(html, encoding="UTF-8")
