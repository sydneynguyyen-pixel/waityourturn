"""Turn the Capitol illustration into cross-stitch charts for the game.
Reads game-assets/capitol-from-screenshot.png, resizes it with macOS sips to a few widths,
and writes data/stitch_capitol.json: {width: [rows]} where each row is a string of
'.' (empty), 'W' (half stitch, the drawing's black lines) and 'w' (full cross, its gold areas).
Run from the project root, then python3 src/build.py."""
import json,os,struct,subprocess,tempfile
SRC="game-assets/capitol-from-screenshot.png";OUT="data/stitch_capitol.json"
def bmp(path):
    b=open(path,"rb").read();off=struct.unpack_from("<I",b,10)[0];w,h=struct.unpack_from("<ii",b,18);bpp=struct.unpack_from("<H",b,28)[0]//8
    flip=h>0;h=abs(h);row=(w*bpp+3)//4*4;px=[]
    for y in range(h):
        o=off+(h-1-y if flip else y)*row;px.append([(b[o+x*bpp+2],b[o+x*bpp+1],b[o+x*bpp]) for x in range(w)])
    return px
sw,sh=[int(l.split(":")[1]) for l in subprocess.check_output(["sips","-g","pixelWidth","-g","pixelHeight",SRC]).decode().splitlines()[1:3]]
out={}
for w in (84,70,56,44):
    h=round(w*sh/sw);t=os.path.join(tempfile.mkdtemp(),"c.bmp")
    subprocess.check_call(["sips","-s","format","bmp","-z",str(h),str(w),SRC,"--out",t],stdout=subprocess.DEVNULL)
    rows=[]
    for r in bmp(t):
        s=""
        for R,G,B in r:
            lum=.3*R+.59*G+.11*B;sat=max(R,G,B)-min(R,G,B)
            s+="." if lum>232 and sat<40 else "W" if lum<105 else "w"
        rows.append(s)
    while rows and not rows[-1].strip("."):rows.pop()
    while rows and not rows[0].strip("."):rows.pop(0)
    out[w]=rows
json.dump(out,open(OUT,"w"))
for r in out[56]:print(r)
