import sys, json
sys.path.insert(0, "/home/claude/ch14/drive/terminal_qc")
import tesr_vision_runner as R, cv2
cfg = json.load(open("/home/claude/ch14/drive/terminal_qc/terminal_qc_config.json"))
roi = cfg["cameras"][0]["rois"][0]
import os; os.chdir("/home/claude/ch14/drive/terminal_qc")
img = cv2.imread("/home/claude/ch14/data/samples_terminal/ng_3343.jpg")
v, c, dbg = R.task_parts_check(img, roi)
o = R._PARTS_SEEN[roi["id"]]["objects"][0]
x1, y1, x2, y2 = o["box"]; H, W = img.shape[:2]
pw, ph = (x2-x1)*0.1, (y2-y1)*0.1
a, b, cc, d = int(max(0, x1-pw)), int(max(0, y1-ph)), int(min(W, x2+pw)), int(min(H, y2+ph))
p1 = img.copy(); cv2.rectangle(p1, (x1, y1), (x2, y2), (0, 140, 255), 14)
cv2.imwrite("/home/claude/ch14/fig/c1.jpg", p1[max(0,b-500):min(H,d+500), max(0,a-350):min(W,cc+350)])
crop = img[b:d, a:cc].copy(); cv2.imwrite("/home/claude/ch14/fig/c2.jpg", crop)
p3 = crop.copy()
for q in o["parts"]:
    cv2.rectangle(p3, (q[0]-a, q[1]-b), (q[2]-a, q[3]-b), (60, 200, 60), 5)
cv2.imwrite("/home/claude/ch14/fig/c3.jpg", p3)
print(v)
