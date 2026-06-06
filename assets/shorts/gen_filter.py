import math

# ---- timeline -------------------------------------------------------------
DUR = 25.0
BEAT = 5.0
HOOK = "ME vs THE WORK WEEK"
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
INK = "0x5A1030"          # deep berry outline color for text borders
BOX = "0xC81E5A@0.9"      # day-label chip

# input index per source PNG (ffmpeg -i order: 0=gradient bg, 1..4 = frames)
F1, F2, F3, F4 = 1, 2, 3, 4

# beats: (day, input, base_size, cy, pop, bAmp, bFreq, swayAmp, swayFreq,
#         jitter, rot, line1, line2)
beats = [
    ("MONDAY",    F1, 720,  980, 0.30, 120, 2.4,  0,   0.0, False,
        "0.05*sin(2*PI*3.0*(t-{S}))", "NEW WEEK", "NEW ME"),
    ("TUESDAY",   F2, 720,  980, 0.30,  85, 2.0, 28,   0.7, False,
        None, "STILL", "GOT THIS"),
    ("WEDNESDAY", F2, 700,  990, 0.28,  55, 1.5, 45,   1.0, False,
        None, "HALFWAY", "THERE..."),
    ("THURSDAY",  F3, 700, 1000, 0.26,  22, 1.0,  0,   0.0, True,
        None, "RUNNING ON", "FUMES"),
    ("FRIDAY",    F4, 760, 1005, 0.34,   6, 0.6,  0,   0.0, False,
        "0.13*sin(2*PI*1.3*(t-{S}))", "I MADE IT", "...BARELY"),
]

# ---- count how many times each input is used (need split) -----------------
use = {}
for b in beats:
    use[b[1]] = use.get(b[1], 0) + 1

lines = []

# background: animated gradient, sized + fps
lines.append("[0:v]format=rgba,fps=30,scale=1080:1920[bg];")

# split sources as needed
src_iter = {}
for idx, n in use.items():
    if n == 1:
        outs = [f"src{idx}_0"]
        lines.append(f"[{idx}:v]format=rgba[{outs[0]}];")
    else:
        outs = [f"src{idx}_{k}" for k in range(n)]
        lines.append(f"[{idx}:v]format=rgba,split={n}" + "".join(f"[{o}]" for o in outs) + ";")
    src_iter[idx] = iter(outs)

prev = "bg"
for j, b in enumerate(beats):
    (day, inp, base, cy, pop, bAmp, bFreq, swayAmp, swayFreq, jit, rot, l1, l2) = b
    S = j * BEAT
    Send = S + BEAT
    src = next(src_iter[inp])

    # dynamic scale: punch-in pop on the cut + tiny continuous heartbeat pulse
    sexpr = (f"{base}*(1+{pop}*exp(-9*max(t-{S},0))*between(t,{S},{S+0.9}))"
             f"*(1+0.025*sin(2*PI*5*t))")
    chain = f"[{src}]scale=w='{sexpr}':h='{sexpr}':eval=frame"
    if rot:
        chain += f",rotate='{rot.format(S=S)}':c=none"
    cj = f"c{j}"
    lines.append(chain + f"[{cj}];")

    # position: centered (auto via overlay_w/h) + bounce + sway + jitter
    bounce = f"{bAmp}*abs(sin(2*PI*{bFreq}*(t-{S})))"
    sway = f"+{swayAmp}*sin(2*PI*{swayFreq}*(t-{S}))" if swayAmp else ""
    jx = "+8*sin(2*PI*22*t)" if jit else ""
    jy = "+6*sin(2*PI*19*t)" if jit else ""
    x = f"(W-overlay_w)/2{sway}{jx}"
    y = f"{cy}-overlay_h/2-{bounce}{jy}"
    out = f"v{j}"
    lines.append(
        f"[{prev}][{cj}]overlay=x='{x}':y='{y}':enable='between(t,{S},{Send})'[{out}];")
    prev = out

# ---- text overlays --------------------------------------------------------
def dt(text, size, x, y, extra=""):
    return (f"drawtext=fontfile={FONT}:text='{text}':fontsize={size}:"
            f"x='{x}':y='{y}'{extra}")

# persistent hook
lines.append(f"[{prev}]" + dt(HOOK, 52, "(w-text_w)/2", "60",
             ":fontcolor=white:bordercolor=" + INK + ":borderw=8") + "[hook];")
prev = "hook"

for j, b in enumerate(beats):
    day, l1, l2 = b[0], b[11], b[12]
    S = j * BEAT
    Send = S + BEAT
    en = f":enable='between(t,{S},{Send})'"
    # day chip springs down from above
    dy = f"200-260*exp(-14*max(t-{S},0))"
    lab = f"d{j}"
    lines.append(f"[{prev}]" + dt(day, 116, "(w-text_w)/2", dy,
        f":fontcolor=white:box=1:boxcolor={BOX}:boxborderw=22{en}") + f"[{lab}];")
    prev = lab
    # phrase lines spring up from below
    py1 = f"1470+320*exp(-14*max(t-{S},0))"
    py2 = f"1590+320*exp(-14*max(t-{S},0))"
    p1 = f"p{j}a"; p2 = f"p{j}b"
    lines.append(f"[{prev}]" + dt(l1, 90, "(w-text_w)/2", py1,
        f":fontcolor=white:bordercolor={INK}:borderw=10{en}") + f"[{p1}];")
    lines.append(f"[{p1}]" + dt(l2, 90, "(w-text_w)/2", py2,
        f":fontcolor=white:bordercolor={INK}:borderw=10{en}") + f"[{p2}];")
    prev = p2

# watermark + final pixel format
lines.append(f"[{prev}]" + dt("@dailysmoothie", 40, "(w-text_w)/2", "1840",
             ":fontcolor=white@0.75") + ",format=yuv420p[vout]")

with open("filter_fast.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
print("wrote filter_fast.txt:", len(lines), "filter lines")
