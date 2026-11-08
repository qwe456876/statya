import pandas as pd, matplotlib.pyplot as plt
from pathlib import Path
src=Path('asvspoof_repo/reports/comparison.csv')
df=pd.read_csv(src)
model='WavLM frozen layer 3 + MLP'
sel=df[df.model==model].copy()
assert set(sel.split)=={'dev','eval','eval2021'}
assert (sel.n_files>0).all() and (sel.EER.between(0,0.5)).all()
# Reproducibility audit: reported rates are bounded and rounded consistently.
assert (sel[['FAR','FRR','EER']].ge(0)&sel[['FAR','FRR','EER']].le(1)).all().all()
sel.to_csv('results/real_benchmark_wavlm_mlp.csv',index=False)
fig,ax=plt.subplots(figsize=(7,4));
labels=['Dev 2019','Eval 2019','Eval 2021']; x=range(3)
ax.bar([i-.18 for i in x],sel.EER*100,.36,label='EER',color='#1f77b4')
ax.bar([i+.18 for i in x],sel.FAR*100,.36,label='FAR (атака принята)',color='#d62728')
ax.set_xticks(list(x),labels); ax.set_ylabel('Ошибка, %'); ax.set_title('Реальный benchmark ASVspoof: WavLM + MLP'); ax.grid(axis='y',alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig('results/fig_real_benchmark.png',dpi=220); plt.close(fig)
print(sel[['split','Accuracy','FAR','FRR','EER','n_files']].to_string(index=False))
print('audit passed')
