# K4 Day 13 — Robotaxi A: LiDAR 3D Object

- Họ và tên: Trịnh Quang Trung
- MSSV: 2A202602096
- Nhóm: chỉ có một người trong báo cáo này (khác hướng dẫn nhóm 3–4 người).

## Nội dung

| File | Nội dung |
| --- | --- |
| `report/K4-DAY13-Nhom01/TEAMMATES.md` | Người làm và vai trò |
| `report/K4-DAY13-Nhom01/PRE-LABEL-REPORT.md` | Báo cáo PointPillars: provenance, ba lượt A/B/C, phép z, ca QC có kiểm soát, nhận xét cá nhân |

## Phần PointPillars

- Trạng thái: `executed-by-group` (chạy trên máy cá nhân, Linux/WSL2 amd64, Docker CPU) bằng gói Student `student-prelabel-amd64.zip` trên PCD KITTI demo (CC BY-NC-SA 3.0).

| Lượt | delta (m) | Pillar XY (m) | n_boxes | mean_z |
| --- | ---: | ---: | ---: | ---: |
| A | 0 | 0.16 | 1 | 0.330 |
| B | 1.73 | 0.16 | 13 | 1.034 |
| C | 1.73 | 0.32 | 6 | 1.091 |

- Ca QC: `case-batch-z` lệch 13/13 hộp cùng −1.805 m nên dừng batch và kiểm phép chuyển z; `case-one-box-z` lệch 1/13 hộp nên kiểm riêng hộp đó.
- File output gốc (JSON/PNG/CSV) giữ ở máy chạy để LC đối chiếu; repo này không chứa chúng.

## Phần cá nhân (CVAT + portal)

Annotation đã Save, v1, feedback QC và phản hồi/v2 được ghi nhận trên CVAT và portal của ca. Repo này không chứa PCD, ảnh hay annotation Robotaxi.
