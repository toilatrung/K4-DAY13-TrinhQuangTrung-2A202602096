"""Phân tích phụ A/B/C từ output thật của runner (chỉ đọc JSON + PCD, không chạy lại model).

Dùng: python3 compare_runs.py <thư mục ket-qua-nhom-01> <demo.pcd>
Viết với sự hỗ trợ của trợ lý AI (Claude Code); logic và số liệu do người nộp kiểm lại.
"""
import glob, json, math, sys
import numpy as np

out, pcd = sys.argv[1], sys.argv[2]
raw = open(pcd, 'rb').read()
body = raw[raw.index(b'DATA binary\n') + len(b'DATA binary\n'):]
a = np.frombuffer(body, dtype=np.dtype([('x', '<f4'), ('y', '<f4'), ('z', '<f4'), ('rgb', '<u4')]))
P = np.stack([a['x'], a['y'], a['z']], 1).astype(float)
RANGE = (0.0, -39.68, -3.0, 69.12, 39.68, 1.0)  # KITTI preset trong preannotate.py
runs = {r: json.load(open(glob.glob(f'{out}/run-{r}/boxes-*.json')[0])) for r in 'ABC'}
zg = runs['A']['z_ground']

print(f'== Điểm trong cửa sổ checkpoint (tổng {len(P)} điểm, z_ground={zg:.3f})')
inxy = (P[:, 0] >= RANGE[0]) & (P[:, 0] <= RANGE[3]) & (P[:, 1] >= RANGE[1]) & (P[:, 1] <= RANGE[4])
for r in 'ABC':
    zm = P[:, 2] - zg - runs[r]['delta']
    inz = (zm >= RANGE[2]) & (zm <= RANGE[5])
    print(f'{r}: delta={runs[r]["delta"]:<4} trong x-y {inxy.sum()}, trong x-y và z {(inxy & inz).sum()}, '
          f'bị cắt vì z>1 m {(inxy & (zm > RANGE[5])).sum()} ({100*(inxy & (zm > RANGE[5])).sum()/inxy.sum():.1f}% điểm trong x-y)')

def footprint(b):
    c, s = math.cos(b['yaw']), math.sin(b['yaw'])
    return c, s
def inside(b, x, y):
    c, s = footprint(b)
    dx, dy = x - b['x'], y - b['y']
    return abs(c*dx + s*dy) <= b['length']/2 and abs(-s*dx + c*dy) <= b['width']/2
def pts_in(b):
    m = np.array([inside(b, x, y) for x, y in P[:, :2]])
    return m & (P[:, 2] >= b['z'] - b['height']/2) & (P[:, 2] <= b['z'] + b['height']/2), m

print('\n== Từng hộp B: đáy, điểm trong hộp, mặt đất cục bộ (z thấp nhất trong footprint)')
print('#  label       x      y    đáy   mặtđất  đáy-mặtđất  điểm_trong_hộp  score')
for i, b in enumerate(runs['B']['boxes']):
    inb, fp = pts_in(b)
    g = np.percentile(P[fp, 2], 5) if fp.sum() else float('nan')
    bot = b['z'] - b['height']/2
    print(f'{i:<2} {b["label"]:<10} {b["x"]:6.2f} {b["y"]:6.2f} {bot:6.2f} {g:7.2f} {bot-g:10.2f} {inb.sum():10d}   {b["score"]:.2f}')

print('\n== Ghép A→B và C→B (tâm hộp nằm trong footprint hộp B)')
for r in 'AC':
    for i, b in enumerate(runs[r]['boxes']):
        hit = [j for j, o in enumerate(runs['B']['boxes']) if inside(o, b['x'], b['y'])]
        print(f'{r}#{i} {b["label"]:<10} ({b["x"]:.2f},{b["y"]:.2f}) score {b["score"]:.2f} -> trong B#{hit if hit else "không"}'
              + (f' ({", ".join(runs["B"]["boxes"][j]["label"] for j in hit)})' if hit else ''))
print('\n== Yaw (độ) A#0 so với B#1:', round(math.degrees(runs['A']['boxes'][0]['yaw']), 1),
      round(math.degrees(runs['B']['boxes'][1]['yaw']), 1))
print('== Lưới BEV: pillar 0.16 ->', round(69.12/0.16), 'x', round(79.36/0.16), '; pillar 0.32 ->', round(69.12/0.32), 'x', round(79.36/0.32))
