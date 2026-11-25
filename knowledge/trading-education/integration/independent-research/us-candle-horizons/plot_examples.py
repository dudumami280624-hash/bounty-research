from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from analyze import read_bars

root = Path(__file__).resolve().parent
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), dpi=170)
for ax, ticker, stamp in zip(axes, ("DAL","NKE"), ("2020-04-30","2022-03-31"), strict=True):
    bars, _ = read_bars(root / "data" / f"{ticker}.json", "monthly", date(2026,11,25))
    k = next(i for i,b in enumerate(bars) if str(b[0]) == stamp)
    entry = bars[k+1][1]
    exit_price = bars[k+12][4]
    change = 100*(exit_price/entry-1)
    for j, (_,o,h,l,c) in enumerate(bars[k-6:k+13], start=-6):
        col = "#168270" if c>=o else "#BC4147"
        ax.vlines(j,l,h,color=col,lw=1.2)
        ax.add_patch(Rectangle((j-.29,min(o,c)),.58,max(abs(c-o),.04),facecolor=col,edgecolor="none"))
    ax.axvspan(-.52,.52,color="#f0be45",alpha=.30,zorder=0)
    ax.scatter(12,exit_price,marker="o",s=32,color="#20344F",zorder=5)
    ax.set(xlim=(-6.8,12.8),xticks=[-6,0,6,12],xlabel="Months from signal",ylabel="Price (USD)")
    ax.set_title(f"{ticker}  |  {stamp[:7]} monthly hammer\n12-month price change: {change:+.1f}%",loc="left",fontweight="bold",fontsize=12)
    ax.spines[["top","right"]].set_visible(False)
    ax.grid(axis="y",linewidth=.55,color="#dbe2ea")
    ax.set_axisbelow(True)
fig.suptitle("The same monthly pattern, two different outcomes",x=.075,y=.97,ha="left",fontsize=17,fontweight="bold")
fig.subplots_adjust(left=.075,right=.98,top=.78,bottom=.2,wspace=.25)
fig.text(.075,.045,"Shaded candle marks the signal. Return runs from next month's open to the close of month 12.",fontsize=9.5)
fig.savefig(root/"US_Monthly_Hammer_DAL_NKE.png",bbox_inches="tight",pad_inches=.24)
