diff --git a/README.md b/README.md
index 9de755268aa480de4cefab726c26e9c340db42b0..877674fbcb36d006f276bdea089f513cf3339ef5 100644
--- a/README.md
+++ b/README.md
@@ -1,2 +1,39 @@
 # GuessTheWord
-This is Yiğit's first coding experience.
+
+Tarayıcıdan oynanabilen, oda tabanlı çok oyunculu kelime tahmin oyunu.
+
+## Yeni Oyun Akışı (Çok Oyunculu)
+- İlk oyuncu (host) bir oda açar ve **tur sayısını belirler**.
+- Diğer oyuncular oda kodu ile kendi cihazlarından aynı odaya katılır.
+- Her turda ipucu gösterilir ve tüm oyuncular yanıtını **bağımsız** gönderir.
+- Bir oyuncu yanıtını gönderince diğer oyuncuların yanıtını göremez.
+- Tur, **herkes yanıtını gönderdikten sonra** otomatik biter.
+- Tur sonunda hedef kelime açıklanır ve puan tablosu oluşur. Doğru bilen ilk 4 oyuncu: **400 / 300 / 200 / 100**.
+- Puanlar tüm turlar boyunca birikir ve son tur sonunda kazanan ilan edilir.
+
+## Lokal Çalıştırma
+```bash
+python -m venv .venv
+source .venv/bin/activate
+pip install -r requirements.txt
+python app.py
+```
+Tarayıcı: `http://localhost:5000`
+
+## Test
+```bash
+python -m unittest -v
+```
+
+## Render.com Deploy
+- Build Command: `pip install -r requirements.txt`
+- Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
+
+> Not: Render Start Command alanına `web:` yazmayın. `web:` sadece `Procfile` formatıdır.
+
+
+## Render Hata Notu (ModuleNotFoundError: multiplayer)
+Eğer deploy logunda `ModuleNotFoundError: No module named 'multiplayer'` görürseniz:
+- Bu sürümde oyun odası mantığı `app.py` içine alındı; ek modül importuna bağımlılık azaltıldı.
+- Render servisinde **Root Directory** alanı boş veya repo kökü olmalı.
+- Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
