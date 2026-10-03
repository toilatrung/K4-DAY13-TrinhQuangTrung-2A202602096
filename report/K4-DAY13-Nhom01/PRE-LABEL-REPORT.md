# Báo cáo thực hành PointPillars — Day 13

Đây là kiểm tra formative. Báo cáo chỉ ghi giá trị lấy từ output thật của nhóm (`ket-qua-nhom-01/`: `smoke.json`, `run-A|B|C/{boxes-*.json, side-*.png, summary.csv}`, `qc-cases/`). File JSON/PNG/CSV giữ ở máy chạy để LC đối chiếu, không nằm trong repo này.

## Nhóm và provenance

- Mã nhóm/phòng: chưa có nhóm đầy đủ (xem `TEAMMATES.md`); thư mục `Nhom01` theo tên output. Thành viên: Trịnh Quang Trung.
- Trạng thái: `executed-by-group` (chạy trên máy cá nhân, không phải máy LC). Báo cáo chỉ có nhận xét của một người; một người đảm nhận mọi vai (khác hướng dẫn nhóm 3–4 người).
- Người chạy: Trịnh Quang Trung (2A202602096); ngày 2026-10-02; Linux (WSL2) x86_64/amd64, 16 CPU, 7 GB RAM, Docker 29.8.0, không dùng GPU.
- Gói chạy: `student-prelabel-amd64.zip` (sha256 khớp `SHA256SUMS.txt`: `f58ca337…37aa9`). Lệnh: `python3 student-bundle.py run --bundle . --out ../ket-qua-nhom-01`. `smoke.json` có status `passed` (docker-load, run-A, run-B, run-C, qc-cases đều passed).
- Image: `day13-pointpillars:lc-20261001-amd64`, ID `sha256:e03983bd922e…2c2`; repo revision `0831856d921609312d42c7582c366e5a311bb7b1`. `smoke.json` ghi `working_tree_dirty: true`, nên không khẳng định bản chạy trùng hoàn toàn với revision này.
- PCD: KITTI Student (đã chuyển đổi, CC BY-NC-SA 3.0), `frame_id` = `demo`, 17238 điểm; sha256 input `3b5ea3da…5d60`.
- Checkpoint: `epoch_160.pth` (PointPillars KITTI có sẵn trong image), sha256 `482dfcf6…b5b1`.
- Phạm vi: cửa sổ phía trước (front ROI), score threshold 0.3 (mặc định runner), giữ cố định ở cả ba lượt.
- Giả định: reflectance thật bị bỏ, kênh thứ tư là hằng, RGB=0; `z_ground` ước lượng từ PCD = 0.075 m (`z_ground` trong JSON). Kết quả không phải benchmark KITTI có intensity thật.

## Ba lượt inference thật

| Lượt | delta (m) | Pillar XY (m) | Số hộp (`n_boxes`) | mean_z (`mean_z`) | File | Quan sát có bằng chứng |
| --- | --- | --- | --- | --- | --- | --- |
| A | 0 | 0.16 | 1 | 0.330 | `run-A/boxes-demo-delta-0-voxel-0.16.json`, `side-…png`, `summary.csv` | Một hộp `vehicles` score 0.32 tại x=13.15, y=−0.45, z=0.33; trên ảnh Side đáy hộp nằm dưới đường z=0 (khoảng −0.4 m) |
| B | 1.73 | 0.16 | 13 | 1.034 | `run-B/boxes-demo-delta-1.73-voxel-0.16.json`, `side-…png`, `summary.csv` | 10 `vehicles` (score 0.50–0.93), 1 `two-wheels` (0.38), 2 `pedestrian` (0.32, 0.34); trải từ x≈3.7 đến x≈55.6 |
| C | 1.73 | 0.32 | 6 | 1.091 | `run-C/boxes-demo-delta-1.73-voxel-0.32.json`, `side-…png`, `summary.csv` | Cả 6 hộp là `pedestrian` (score 0.30–0.81), nằm ở x≈9–34; không còn `vehicles` |

- **A/B (chỉ đổi delta 0 → 1.73):** A có 1 hộp, B có 13 hộp và đủ ba class. Trên ảnh Side, A chỉ có một hộp quanh x≈11–15 m, trong khi B có hộp rải suốt x≈2–58 m, kể cả các hộp ở x>30 m mà A không có. Đây là chạy lại model trên input đã dịch z, không phải tịnh tiến hộp cũ, nên không thể đối chiếu A và B bằng cách trừ z của từng hộp. Hộp duy nhất của A (x=13.15, y=−0.45) không có hộp B trùng vị trí: hộp B gần nhất là x=14.77, y=−1.08, kích thước và score khác. Điều chưa chắc: B có nhiều hộp và score cao hơn nhưng không có nhãn chuẩn, nên chưa kết luận B đúng hơn A; quan sát chỉ cho thấy delta=1.73 làm đầu ra của checkpoint KITTI khác hẳn.
- **B/C (chỉ đổi pillar 0.16 → 0.32):** số hộp giảm 13 → 6, 10 `vehicles` và `two-wheels` của B biến mất, còn lại 6 `pedestrian`. Các hộp C có chiều dài khoảng 0.6–1.1 m, trong khi các `vehicles` ở B dài khoảng 3.1–4.2 m. Trên ảnh Side, các hộp C hẹp và cao ở x≈9–13 m, đúng vùng B có các xe (x=8.09, 9.38, 14.77). Đây là dấu hiệu pillar thô làm mất chi tiết nhưng chưa phải bằng chứng model nhận sai class, vì không có ground truth. Không dùng quan sát này để nói C hoặc B tốt hơn.
- **ROI và Side:** chỉ xét cửa sổ phía trước (ảnh Side hiển thị x −20…70 m, các hộp đều ở x>0), nên đối tượng phía sau hoặc ngoài ROI không được dự đoán và không được tính là model bỏ sót. Ảnh Side là chiếu x–z nên chồng các vật khác y, và không cho kiểm yaw hay đối chiếu đầu xe.
- **Chưa đủ cơ sở để import:** mọi JSON ở đây là PCD KITTI minh họa (`frame_id=demo`), không import vào CVAT/Robotaxi. Với Robotaxi, chỉ dùng prediction do portal nạp đúng frame. Cần kiểm tiếp bằng ảnh camera và nhiều góc 3D trước khi tin bất kỳ hộp nào.

## Phép đổi z và ca QC có kiểm soát — không import CVAT

Phép đổi z thuận/ngược của bài:

```
z_model  = z_source - z_ground - delta
z_source = z_model  + z_ground + delta
```

Điểm nguồn được dịch trước khi vào model; hộp xuất ra đã được chuyển ngược về hệ nguồn, nên JSON đọc trực tiếp, không cộng thêm delta. Đổi delta trước inference khác với dịch hộp sau inference: ở trường hợp đầu model nhìn thấy dữ liệu khác nên số hộp, class, vị trí có thể đổi (A 1 hộp so với B 13 hộp); ở trường hợp sau, mọi hộp chỉ tịnh tiến đồng loạt. Với B: `height_offset_m` = 0.075 + 1.73 = 1.805 m (`qc-cases/manifest.json`).

Nguồn các ca: `boxes-demo-delta-1.73-voxel-0.16.json` (B, 13 hộp). So sánh từng hộp giữa từng ca và B:

| Ca | Số hộp lệch z / tổng hộp | Lượng lệch | Class/x/y/yaw/kích thước có đổi? | Hành động | Bằng chứng |
| --- | --- | --- | --- | --- | --- |
| case-correct | 0/13 | 0 | Không | Không phát hiện lỗi z; chỉ là bản sao dùng làm mốc so sánh, không phải nhãn đúng | `qc-cases/case-correct.json`, `side-correct.png` |
| case-batch-z | 13/13 | −1.805 m ở mỗi hộp | Không (chỉ z đổi) | Dừng sửa tay, báo LC kiểm phép chuyển z (thiếu phép nghịch delta + z_ground) | `case-batch-z.json`, `side-batch-z.png` |
| case-one-box-z | 1/13 (hộp đầu tiên) | −1.805 m | Không (chỉ z đổi) | Không dừng batch; kiểm riêng hộp đó bằng nhiều góc và ảnh camera | `case-one-box-z.json`, `side-one-box-z.png` |

Các ca này do helper tạo có chủ đích từ prediction B (`qc-cases/manifest.json`, `training_only: true`), không phải inference riêng và không phải nhãn đúng. Chúng không được import vào CVAT.

## Nhận xét cá nhân

### Trịnh Quang Trung (2A202602096)

- **Vai trò:** vận hành lệnh chạy gói Student cho cả ba lượt A/B/C trên máy cá nhân (trạng thái `executed-by-group`), đọc CSV/JSON/Side và ghi log.
- **Quan sát A/B/C:** A→B (chỉ đổi delta) làm số hộp 1 → 13 (`summary.csv` của run-A và run-B). B→C (chỉ đổi pillar) làm 13 → 6 và mọi hộp còn lại là `pedestrian` với chiều dài 0.59–1.07 m (`run-C/boxes-…json`), trong khi `vehicles` ở B dài 3.1–4.2 m.
- **Phép z:** input được dịch theo delta sau khi trừ `z_ground`; hộp trả về nguồn bằng `z_model + z_ground + delta`, với B là +1.805 m. Vì vậy A và B không thể so bằng cách trừ z từng hộp.
- **Quyết định ca lỗi:** `case-batch-z` có 13/13 hộp cùng lệch −1.805 m và các trường khác giữ nguyên nên dừng sửa tay và kiểm phép chuyển. `case-one-box-z` chỉ có 1/13 hộp lệch nên kiểm riêng hộp đó, không dừng batch.
- **Điều chưa chắc:** không có ground truth nên chưa biết cấu hình nào đúng hơn; chưa đối chiếu ảnh camera cho PCD KITTI minh họa; `working_tree_dirty: true` trong `smoke.json` nên chưa chứng minh bản chạy trùng revision. Ảnh Side chưa đủ để kết luận yaw hay class.

## LC ghi nhận riêng

(Để LC điền.)
