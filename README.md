 # GuessTheWord
-This is Yiğit's first coding experience.
+
+Tarayıcıdan oynanabilen kelime tahmin oyunu.
+
+## Oyun Kuralları
+- Sistem gizli bir kelime seçer ve kelime uzunluğuna göre harf ipucu verir.
+- Oyuncular sırayla birer tahmin yapar.
+- Doğru bilen ilk 4 oyuncu sırasıyla **400 / 300 / 200 / 100** puan alır.
+- Tur sonunda en yüksek puanlı oyuncu kazanır.
+
+## Lokal Çalıştırma
+Statik bir web uygulamasıdır. Basit bir HTTP sunucusu ile açabilirsiniz:
+
+```bash
+python -m http.server 8000
+```
+
+Ardından tarayıcıda `http://localhost:8000` adresini açın.
+
+## Test
+Python oyun mantığı testleri:
+
+```bash
+python -m unittest -v
+```
+
+## Ücretsiz şekilde internete yayınlama (GitHub Pages)
+Web siteniz olmasa bile bu oyun için ücretsiz bir adres alabilirsiniz:
+
+1. Bu projeyi GitHub'a yükleyin.
+2. GitHub'da repo sayfasında **Settings → Pages** bölümüne gidin.
+3. **Source** olarak `Deploy from a branch` seçin.
+4. Branch olarak `main` (veya projenizin ana branch'i), folder olarak `/ (root)` seçin.
+5. **Save** dedikten sonra birkaç dakika içinde size bir link verilir:
+   - Örnek: `https://kullaniciadi.github.io/GuessTheWord/`
+6. Bu linki paylaşarak oyunu tarayıcıdan oynatabilirsiniz.
+
+> Not: Bu yaklaşım tamamen ücretsizdir ve backend gerekmez.
