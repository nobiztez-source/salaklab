# สลากแล็บ: หน้าแชร์ผลสลาก

Repository นี้สร้างหน้า GitHub Pages พร้อมรูป Open Graph ขนาด 1200 × 630 พิกเซล
จากผลล่าสุดของแอป Google Apps Script แล้วพาผู้ใช้ไปยังแอปหลัก
โค้ดของแอปหลักไม่ได้อยู่ใน repository นี้

## รันในเครื่อง

ต้องมี Python 3 และ Chrome หรือ Chromium รวมถึงฟอนต์ใน `fonts/`
ไม่ต้องติดตั้ง Python package เพิ่มเติม

```sh
GITHUB_REPOSITORY=nobiztez-source/salaklab python3 build.py
```

คำสั่งนี้อ่านผลจาก endpoint `?api=latest` ที่กำหนดใน `build.py`
จะสร้างใหม่เมื่อรางวัลที่แสดงเปลี่ยน หรือรูปผลลัพธ์หายหรือว่างเปล่า
ใช้ `--force` เมื่อต้องการสร้างใหม่แม้ผลรางวัลไม่เปลี่ยน

สำหรับการทดสอบด้วยข้อมูลที่บันทึกไว้โดยไม่เรียก API:

```sh
GITHUB_REPOSITORY=nobiztez-source/salaklab LATEST_JSON=data.json python3 build.py --force
```

ผลลัพธ์คือ `index.html`, `data.json` และ `og-YYYYMMDD.png`
ตัวสร้างจะเก็บไฟล์เดิมไว้ระหว่างรอ Chrome สร้างรูปใหม่
และจะไม่แทนที่ไฟล์ผลลัพธ์เมื่อการสร้างรูปล้มเหลว

## ทดสอบ

```sh
python3 -m unittest discover -s tests -v
python3 -m py_compile build.py
```

Unit tests ใช้ข้อมูลจำลองและจำลอง Chrome จึงไม่ต้องเชื่อมต่อเครือข่าย
ควรรันคำสั่งสร้างจริงและตรวจรูปด้วยเมื่อแก้รูปลักษณ์หน้าแชร์

## GitHub Actions

`.github/workflows/og.yml` ตรวจผลตามตารางเวลา และเปิดให้รันเองด้วย
`workflow_dispatch` การ push โค้ดหรือฟอนต์จะบังคับสร้างใหม่ เพื่อให้การแก้
รูปแบบหน้าแชร์มีผลแม้ยังไม่มีงวดใหม่ ทุกครั้งจะรัน unit tests ก่อนสร้าง
และ commit ไฟล์ผลลัพธ์เมื่อมีการเปลี่ยนแปลง

การ push ไป `main` อาจทำให้ระบบเดิมเผยแพร่หน้า GitHub Pages อัตโนมัติ
ควรตรวจ diff และผลทดสอบก่อนนำการแก้ไขขึ้น repository
