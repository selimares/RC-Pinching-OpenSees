from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
EXP = ROOT/"data"/"experimental.csv"
MOD = ROOT/"results"/"opensees_response.csv"
FIG = ROOT/"results"/"experimental_vs_opensees.png"
MET = ROOT/"results"/"metrics.csv"

def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    return (np.array([float(r["displacement_mm"]) for r in rows]),
            np.array([float(r["force_kN"]) for r in rows]))

def interp_branchwise(x, xd, yd):
    out=np.full(len(x),np.nan)
    for i, target in enumerate(x):
        c=np.where(((xd[:-1]<=target)&(target<=xd[1:])) |
                   ((xd[:-1]>=target)&(target>=xd[1:])))[0]
        if len(c):
            j=c[np.argmin(np.minimum(abs(xd[c]-target),abs(xd[c+1]-target)))]
            if abs(xd[j+1]-xd[j])<1e-12: out[i]=(yd[j]+yd[j+1])/2
            else: out[i]=yd[j]+(target-xd[j])/(xd[j+1]-xd[j])*(yd[j+1]-yd[j])
    return out

def abs_energy(d,f):
    return float(np.sum(np.abs(0.5*(f[1:]+f[:-1])*(d[1:]-d[:-1]))))

de,fe=read_csv(EXP); dm,fm=read_csv(MOD)
fp=interp_branchwise(de,dm,fm)
v=np.isfinite(fp)
rmse=float(np.sqrt(np.mean((fp[v]-fe[v])**2)))
ssres=float(np.sum((fe[v]-fp[v])**2)); sst=float(np.sum((fe[v]-np.mean(fe[v]))**2))
r2=float(1-ssres/sst) if sst else np.nan
peak_err=float(100*(np.max(abs(fm))-np.max(abs(fe)))/np.max(abs(fe)))
er=abs_energy(de,fe); em=abs_energy(dm,fm); energy_ratio=em/er if er else np.nan

with open(MET,"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["metric","value","unit"])
    w.writerow(["RMSE",rmse,"kN"]); w.writerow(["R2",r2,"-"])
    w.writerow(["Peak force error",peak_err,"%"])
    w.writerow(["Energy ratio",energy_ratio,"model / experiment"])

plt.figure(figsize=(9,6))
plt.plot(de,fe,label="Experimental",linewidth=1.6)
plt.plot(dm,fm,label="OpenSeesPy",linewidth=1.3)
plt.axhline(0,linewidth=.7); plt.axvline(0,linewidth=.7)
plt.xlabel("Displacement (mm)"); plt.ylabel("Force (kN)")
plt.title("Experimental vs OpenSeesPy Hysteresis Response")
plt.grid(True,alpha=.25); plt.legend(); plt.tight_layout()
plt.savefig(FIG,dpi=300,bbox_inches="tight"); plt.close()
print(f"RMSE={rmse:.3f} kN | R2={r2:.4f} | peak error={peak_err:.2f}% | energy ratio={energy_ratio:.4f}")
