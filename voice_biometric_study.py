#!/usr/bin/env python3
import argparse, json, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc


def eer(y_true, scores):
    fpr, tpr, thr = roc_curve(y_true, scores, pos_label=1)
    fnr = 1-tpr
    i = np.nanargmin(np.abs(fpr-fnr))
    return float((fpr[i]+fnr[i])/2), float(thr[i])


def metrics(genuine, impostor, bona_fide, attacks, threshold):
    far = np.mean(impostor >= threshold)
    frr = np.mean(genuine < threshold)
    apcer = np.mean(attacks >= threshold)
    bpcer = np.mean(bona_fide < threshold)
    return dict(FAR=far, FRR=frr, APCER=apcer, BPCER=bpcer)


def simulate(seed=20261108, n=240):
    rng = np.random.default_rng(seed)
    genuine = np.clip(rng.normal(.82,.07,n),0,1)
    impostor = np.clip(rng.normal(.34,.12,n),0,1)
    bona = np.clip(rng.normal(.80,.08,n),0,1)
    attacks = {
      'replay': np.clip(rng.normal(.67,.12,n),0,1),
      'converted': np.clip(rng.normal(.73,.10,n),0,1),
      'synthetic': np.clip(rng.normal(.77,.09,n),0,1),
      'deepfake': np.clip(rng.normal(.79,.08,n),0,1),
    }
    # threshold calibrated on bona fide vs impostor at EER
    y=np.r_[np.ones(n),np.zeros(n)]; s=np.r_[genuine,impostor]
    e,t=eer(y,s)
    rows=[]
    for name,a in attacks.items():
        m=metrics(genuine,impostor,bona,a,t); m.update(attack=name, threshold=t, EER=e); rows.append(m)
    # PAD score is independent synthetic liveness score; higher=live
    pad_bona=np.clip(rng.normal(.82,.08,n),0,1)
    pad_attack={k:np.clip(rng.normal(mu,.10,n),0,1) for k,mu in [('replay',.28),('converted',.38),('synthetic',.45),('deepfake',.40)]}
    pad_t=.60
    rows_pad=[]
    for name,a in pad_attack.items():
        m=metrics(genuine,impostor,pad_bona,a,pad_t); m.update(attack=name, threshold=pad_t, EER=np.nan); rows_pad.append(m)
    return pd.DataFrame(rows), pd.DataFrame(rows_pad), dict(genuine=genuine, impostor=impostor, attacks=attacks, threshold=t, pad_bona=pad_bona, pad_attack=pad_attack, pad_threshold=pad_t)


def main(out):
    os.makedirs(out,exist_ok=True)
    base,pad,d=simulate()
    base.to_csv(os.path.join(out,'results_asv.csv'),index=False)
    pad.to_csv(os.path.join(out,'results_pad.csv'),index=False)
    summary=pd.DataFrame({'condition':base.attack,'APCER_before':base.APCER,'APCER_PAD':pad.APCER,'BPCER_PAD':pad.BPCER})
    summary.to_csv(os.path.join(out,'summary.csv'),index=False)
    # figure 1: architecture
    fig,ax=plt.subplots(figsize=(10,2.4)); ax.axis('off')
    boxes=['Audio input','ASV embedding\n+ cosine score','Threshold','PAD\n(liveness)','Decision']
    for i,b in enumerate(boxes):
        ax.text(i,0.5,b,ha='center',va='center',fontsize=10,bbox=dict(boxstyle='round,pad=.5',fc='#eaf2f8',ec='#2c3e50'))
        if i<len(boxes)-1: ax.annotate('',xy=(i+.75,.5),xytext=(i+.25,.5),arrowprops=dict(arrowstyle='->',lw=1.5))
    ax.set_xlim(-.5,4.5); ax.set_ylim(0,1); fig.tight_layout(); fig.savefig(os.path.join(out,'fig_architecture.png'),dpi=220); plt.close(fig)
    # figure 2: attack APCER
    fig,ax=plt.subplots(figsize=(7,4)); x=np.arange(len(base)); w=.36
    ax.bar(x-w/2,base.APCER,w,label='Только ASV',color='#c0392b'); ax.bar(x+w/2, pad.APCER,w,label='PAD APCER',color='#2980b9')
    ax.set_xticks(x,['Replay','Voice conversion','Синтез','Deepfake']); ax.set_ylabel('Доля ошибок'); ax.set_ylim(0,1); ax.grid(axis='y',alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(os.path.join(out,'fig_apcer.png'),dpi=220); plt.close(fig)
    # figure 3: score distributions
    fig,ax=plt.subplots(figsize=(7,4));
    ax.hist(d['genuine'],bins=25,alpha=.55,label='Подлинная речь',density=True); ax.hist(d['impostor'],bins=25,alpha=.55,label='Самозванец',density=True)
    for k,v in d['attacks'].items(): ax.hist(v,bins=25,alpha=.25,label={'replay':'Replay','converted':'Voice conversion','synthetic':'Синтез','deepfake':'Deepfake'}[k],density=True)
    ax.axvline(d['threshold'],color='black',ls='--',label=f"Порог = {d['threshold']:.3f}"); ax.set_xlabel('Коэффициент сходства'); ax.set_ylabel('Плотность'); ax.legend(fontsize=8,ncol=2); fig.tight_layout(); fig.savefig(os.path.join(out,'fig_scores.png'),dpi=220); plt.close(fig)
    with open(os.path.join(out,'run_metadata.json'),'w') as f: json.dump({'seed':20261108,'n_per_condition':240,'asv_threshold':d['threshold'],'pad_threshold':d['pad_threshold']},f,indent=2)
    print(base.to_string(index=False))
    print('ASV EER:', base.EER.iloc[0], 'threshold:', d['threshold'])

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='results'); args=ap.parse_args(); main(args.out)
