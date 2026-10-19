"""Remove a static baked-in sticker/text box from a video by harmonic (Laplace) inpainting, frame by
frame, directly on yuv420p planes (colours stay bit-exact outside the patch). A 4 px luma / 2 px chroma
ring around the hole is blended with a lightly blurred copy so the seam is not a hard line.
Built for the B&F TikTok series (first used on v001, 2026-10-16). A soft smudge can remain: cover the
area with a glass card/pill in the edit (cover box = sticker + ~8 px each side, in 1080x1920 terms).

Usage (normally via tools/clean.py):
  ffmpeg ... -pix_fmt yuv420p -f rawvideo - | python sticker_fill.py W H X Y BW BH [X Y BW BH ...] | ffmpeg -f rawvideo ...
  W H = frame size; X Y BW BH = sticker box in SOURCE pixels (several boxes allowed). Needs numpy + scipy.
  STICKER_TEXTURE=auto|below|above|none re-grains the smooth fill with the fine texture of the strip just
  below (or above) the box, so gravel/sky/fabric keeps its grain (default auto = below if it fits).
"""
import sys, numpy as np
import os
import scipy.sparse as sp, scipy.sparse.linalg as spl
from scipy.ndimage import uniform_filter
TEXTURE=os.environ.get('STICKER_TEXTURE','auto')  # auto|below|above|none: re-grain the fill from a neighbouring strip

class Filler:
    def __init__(s, x0, x1, y0, y1, feather, H=None, grain=False):
        s.x0,s.x1,s.y0,s.y1,s.F = x0,x1,y0,y1,feather
        s.donor=None
        if grain and TEXTURE!='none' and H:
            hh=y1-y0+1
            below=y1+3+hh < H-2; above=y0-3-hh > 2
            if TEXTURE in('auto','below') and below: s.donor=y1+3
            elif TEXTURE in('auto','above') and above: s.donor=y0-3-hh
        h,w = y1-y0+1, x1-x0+1; s.h,s.w=h,w
        N=h*w; idx=np.arange(N).reshape(h,w)
        r=[idx.ravel()]; c=[idx.ravel()]; v=[np.full(N,4.0)]
        for a,b in (((slice(1,None),slice(None)),(slice(None,-1),slice(None))),
                    ((slice(None,-1),slice(None)),(slice(1,None),slice(None))),
                    ((slice(None),slice(1,None)),(slice(None),slice(None,-1))),
                    ((slice(None),slice(None,-1)),(slice(None),slice(1,None)))):
            r.append(idx[a].ravel()); c.append(idx[b].ravel()); v.append(np.full(idx[a].size,-1.0))
        A=sp.csc_matrix((np.concatenate(v),(np.concatenate(r),np.concatenate(c))),shape=(N,N))
        s.solve=spl.factorized(A)
        F=feather
        if F>0:
            ys,ye,xs,xe=y0-F-2,y1+F+3,x0-F-2,x1+F+3
            s.ring=(ys,ye,xs,xe)
            yy,xx=np.mgrid[ys:ye,xs:xe]
            dx=np.maximum(np.maximum(x0-xx,xx-x1),0); dy=np.maximum(np.maximum(y0-yy,yy-y1),0)
            inside=(dx==0)&(dy==0)
            din=np.minimum(np.minimum(xx-x0,x1-xx),np.minimum(yy-y0,y1-yy))
            dout=np.maximum(dx,dy)
            s.wgt=np.where(inside,np.clip(1-din/F,0,1),np.clip(1-dout/F,0,1))*0.8
    def __call__(s, P):
        f=P.astype(np.float64); x0,x1,y0,y1=s.x0,s.x1,s.y0,s.y1
        b=np.zeros((s.h,s.w))
        b[0,:]+=f[y0-1,x0:x1+1]; b[-1,:]+=f[y1+1,x0:x1+1]
        b[:,0]+=f[y0:y1+1,x0-1]; b[:,-1]+=f[y0:y1+1,x1+1]
        f[y0:y1+1,x0:x1+1]=s.solve(b.ravel()).reshape(s.h,s.w)
        if s.F>0:
            ys,ye,xs,xe=s.ring
            reg=f[ys-2:ye+2,xs-2:xe+2]
            k=np.array([1,4,6,4,1],float)/16
            t=sum(k[i]*reg[:,i:i+reg.shape[1]-4] for i in range(5))
            t=sum(k[i]*t[i:i+t.shape[0]-4,:] for i in range(5))
            core=f[ys:ye,xs:xe]
            f[ys:ye,xs:xe]=core*(1-s.wgt)+t*s.wgt
        if s.donor is not None:
            d=P[s.donor:s.donor+s.h, x0:x1+1].astype(np.float64)
            hp=np.clip(d-uniform_filter(d,size=7,mode='reflect'),-22,22)
            yy,xx=np.mgrid[0:s.h,0:s.w]
            edge=np.minimum(np.minimum(yy,s.h-1-yy),np.minimum(xx,s.w-1-xx))
            m=np.clip((edge+1)/3.0,0,1)
            f[y0:y1+1,x0:x1+1]+=hp*m
        return np.clip(np.rint(f),0,255).astype(np.uint8)

if __name__=="__main__":
    W,H=int(sys.argv[1]),int(sys.argv[2])
    boxes=[int(v) for v in sys.argv[3:]]
    if not boxes or len(boxes)%4: sys.exit("usage: sticker_fill.py W H X Y BW BH [X Y BW BH ...]")
    M=4
    fl=[]
    for i in range(0,len(boxes),4):
        x,y,bw,bh=boxes[i:i+4]
        x0,y0=max(6,(x-M)//2*2),max(6,(y-M)//2*2); x1,y1=min(W-7,x+bw+M),min(H-7,y+bh+M)
        x1=x1 if (x1-x0+1)%2==0 else x1+1; y1=y1 if (y1-y0+1)%2==0 else y1+1
        fl.append((Filler(x0,x1,y0,y1,1,H=H,grain=True),Filler(x0//2,(x1-1)//2,y0//2,(y1-1)//2,2)))
    ysz=W*H; csz=(W//2)*(H//2); fsz=ysz+2*csz
    inp=sys.stdin.buffer; out=sys.stdout.buffer; n=0
    while True:
        buf=inp.read(fsz)
        if len(buf)<fsz: break
        a=np.frombuffer(buf,np.uint8)
        Y=a[:ysz].reshape(H,W); U=a[ysz:ysz+csz].reshape(H//2,W//2); V=a[ysz+csz:].reshape(H//2,W//2)
        for LY,LC in fl: Y=LY(Y); U=LC(U); V=LC(V)
        out.write(Y.tobytes()); out.write(U.tobytes()); out.write(V.tobytes()); n+=1
    sys.stderr.write(f"sticker_fill: {n} frames, {len(fl)} box(es)\n")
