import subprocess
import scriptcontext as sc
import Rhino

subprocess.call(["python", "-m", "pip", "install", "requests"])

ghdoc = sc.doc
file_path = ghdoc.Path
print(file_path)
