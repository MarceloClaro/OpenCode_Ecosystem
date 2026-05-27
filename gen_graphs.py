import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, os
od = r"C:\Users\marce\OneDrive\Documentos\Antiprojeto UFC\graficos_dca"
os.makedirs(od, exist_ok=True)
np.random.seed(42)

# A: Duffing H0 semilog
def dq(g,q0,T=50,dt=0.05):
    N=int(T/dt);q=np.zeros(N);p=np.zeros(N);q[0]=q0
    for i in range(N-1):
        k1q,k1p=p[i],q[i]-q[i]**3-g*p[i]
        mq,mp=q[i]+.5*dt*k1q,p[i]+.5*dt*k1p
        k2q,k2p=mp,mq-mq**3-g*mp
        mq,mp=q[i]+.5*dt*k2q,p[i]+.5*dt*k2p
        k3q,k3p=mp,mq-mq**3-g*mp
        mq,mp=q[i]+dt*k3q,p[i]+dt*k3p
        k4q,k4p=mp,mq-mq**3-g*mp
        q[i+1]=q[i]+dt/6*(k1q+2*k2q+2*k3q+k4q)
        p[i+1]=p[i]+dt/6*(k1p+2*k2p+2*k3p+k4p)
    H0=.5*p**2+.25*q**4-.5*q**2
    return np.arange(N)*dt, H0

fig,ax=plt.subplots(1,3,figsize=(12,4))
for i,g in enumerate([.01,.1,.5]):
    for q0 in [.5,-.5,1.2,-1.2]:
        t,H0=dq(g,q0,T=50); ax[i].semilogy(t,np.abs(H0)+1e-16,alpha=.6,lw=.4)
    ax[i].set_title(f'gamma={g}');ax[i].set_xlabel('t');ax[i].set_ylabel('|H0(t)|');ax[i].grid(1,alpha=.3)
fig.suptitle('Duffing: H0(t) — Escala Semilog')
plt.tight_layout();plt.savefig(os.path.join(od,'duffing_h0_semilog.png'),dpi=100);plt.close()
print("A OK")

# B: Basins (ultra coarse)
q0s=np.linspace(-2,2,20);p0s=np.linspace(-1.5,1.5,15);bm=np.zeros((15,20))
for i,p0 in enumerate(p0s):
    for j,q0 in enumerate(q0s):
        qq,pp=q0,p0
        for _ in range(500):
            k1=pp;k2=qq-qq**3-.1*pp;qq+=.02*(k1+k2)/2;pp+=.02*(k2-.1*pp)
        bm[i,j]=1 if qq>0 else -1
fig,ax=plt.subplots(figsize=(7,5))
ax.imshow(bm,extent=[q0s[0],q0s[-1],p0s[0],p0s[-1]],origin='lower',aspect='auto',cmap='RdBu',alpha=.8)
ax.set_xlabel('q0');ax.set_ylabel('p0');ax.set_title('Bacias de Atracao — Duffing (gamma=0.1)')
plt.tight_layout();plt.savefig(os.path.join(od,'duffing_bacias.png'),dpi=100);plt.close()
print("B OK")

# C: EDE MC vs FP
om,ka,sg,ep=1.,.3,.5,.5
b=lambda th:om-ka*np.sin(th);a=lambda th:sg*(1+ep*np.cos(th))
Nt,Ti,dt=300,20,.04;fv=[]
for s in range(Nt):
    np.random.seed(s);Ns=int(Ti/dt);th=np.zeros(Ns);th[0]=np.random.uniform(0,2*np.pi)
    for i in range(Ns-1):
        dW=np.sqrt(dt)*np.random.normal()
        tp=th[i]+b(th[i])*dt+a(th[i])*dW
        th[i+1]=th[i]+.5*(b(th[i])+b(tp))*dt+.5*(a(th[i])+a(tp))*dW
    fv.extend(th[-int(Ns*.3):])
Ng=80;dth=2*np.pi/Ng;M=np.zeros((Ng,Ng))
for i in range(Ng):
    th=i*dth;dr=b(th);df=.5*a(th)**2
    ip=(i+1)%Ng;im=(i-1)%Ng
    M[i,im]+=df/dth**2+dr/(2*dth);M[i,i]-=2*df/dth**2;M[i,ip]+=df/dth**2-dr/(2*dth)
ev,evc=np.linalg.eig(M.T);rs=np.abs(evc[:,np.argmin(np.abs(ev))].real)
rs/=np.sum(rs)*dth;tg=np.linspace(0,2*np.pi,Ng)
hist,bins=np.histogram(np.array(fv),bins=40,range=(0,2*np.pi),density=True);bc=(bins[:-1]+bins[1:])/2
fig,ax=plt.subplots(figsize=(10,5))
ax.bar(bc,hist,width=.12,alpha=.4,label='MC',color='#1f77b4')
ax.plot(tg,rs,'r-',lw=2,label='F-P');ax.set_xlabel('theta');ax.set_ylabel('rho');ax.legend();ax.grid(1,alpha=.3)
ax.set_title('EDE: Monte Carlo vs Fokker-Planck')
plt.tight_layout();plt.savefig(os.path.join(od,'ede_mc_vs_fp.png'),dpi=100);plt.close()
print("C OK")

# D: Current J*
Js=np.zeros(Ng)
for i in range(Ng):
    ip=(i+1)%Ng;im=(i-1)%Ng
    dar=(a(tg[ip])*rs[ip]-a(tg[im])*rs[im])/(2*dth)
    Js[i]=b(i*dth)*rs[i]-.5*a(i*dth)*dar
fig,ax=plt.subplots(figsize=(10,4))
ax.plot(tg,Js,'b-',lw=2);ax.axhline(0,color='gray',ls='--',lw=.8)
ax.set_xlabel('theta');ax.set_ylabel('J*');ax.set_title('Corrente Estacionaria');ax.grid(1,alpha=.3)
Jm=np.mean(Js)
ax.text(.5,.9,f'<J*> = {Jm:.4f} (nao-nula = NESS)',transform=ax.transAxes,fontsize=11,ha='center',bbox=dict(boxstyle='round',facecolor='wheat',alpha=.8))
plt.tight_layout();plt.savefig(os.path.join(od,'ede_corrente_j.png'),dpi=100);plt.close()
print("D OK")
print("ALL DONE")
