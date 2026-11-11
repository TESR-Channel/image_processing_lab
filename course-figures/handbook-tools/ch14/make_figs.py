from PIL import Image, ImageDraw, ImageFont
import os
O = "/home/claude/ch14/out/"
def save(im, name, w=1200):
    im = im.convert("RGB")
    if im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    p = O + name
    if name.endswith(".jpg"): im.save(p, quality=80, optimize=True)
    else: im.quantize(160, method=Image.Quantize.MEDIANCUT).save(p, optimize=True)
    print(name, im.size, os.path.getsize(p) // 1024, "KB")
def crop(path, box, s=1): 
    return Image.open(path).crop(tuple(int(v * s) for v in box))
def side(ims, gap=24, bg=(255, 255, 255)):
    h = min(i.height for i in ims)
    ims = [i.resize((round(i.width * h / i.height), h), Image.LANCZOS) for i in ims]
    W = sum(i.width for i in ims) + gap * (len(ims) - 1)
    out = Image.new("RGB", (W, h), bg); x = 0
    for i in ims: out.paste(i, (x, 0)); x += i.width + gap
    return out
F = "/home/claude/ch14/fig/"
for n in ("concept", "route", "folder"):
    save(Image.open(F + n + ".png"), "tb2_%s.png" % n)
save(Image.open("/home/claude/ch14/old/tb_problem.jpg"), "tb2_problem.jpg")
save(Image.open("/home/claude/ch14/old/tb_trainer1.jpg"), "tb2_trainer1.jpg")
T = "/home/claude/ch14/trainer_shots/"
save(crop(T + "01_crop_dialog_th.png", (320, 222, 880, 680)), "tb2_crop_dialog.png", 900)
save(crop(T + "02_new_project_from_crops_th.png", (40, 170, 1160, 570)), "tb2_new_project.png")
save(crop(T + "03_crop_with_screw_boxes_th.png", (290, 125, 910, 600)), "tb2_label_screw.png", 900)
S = "/home/claude/ch14/shots_t2/"
save(crop(S + "s1_addmodel.png", (370, 190, 1130, 640), 2), "tb2_addmodel.png", 1100)
canvas = crop(S + "s5_tall.png", (440, 125, 990, 865), 2)
panel = crop(S + "s5_tall.png", (1213, 140, 1490, 1030), 2)
save(side([canvas, panel]), "tb2_panel.jpg")
ng = crop(S + "s3_ng.png", (232, 50, 1200, 600), 2)
save(ng, "tb2_step_ng.jpg")
okk = crop(S + "s4_ok.png", (440, 130, 990, 860), 2); ngk = crop(S + "s3_ng.png", (440, 130, 990, 860), 2)
save(side([ngk, okk]), "tb2_ng_ok.jpg")
R = "/tmp/claude-0/rec_t/"
def rec(name, box): return Image.open(R + name).crop(box)
import glob
