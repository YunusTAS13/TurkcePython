# TürkçePython 🇹🇷

**Sürüm: 1.1**

Tamamen Türkçe sözdizimli bir programlama dili — Python 3.12+ üzerinde çalışır.

---

## Kurulum ve Kullanım

### 1. Gereksinimler
- Python 3.12 veya üzeri
- Başka hiçbir kütüphane gerekmez (sadece standart Python)

### 2. Dosya çalıştırma
```bash
python turkce.py dosya.tr
```

### 3. İnteraktif mod (REPL)
```bash
python turkce.py
```

### 4. Hata ayıklama — dönüştürülmüş Python kodunu görmek için
```bash
TURKCE_DEBUG=1 python turkce.py dosya.tr
```

---

## Sözdizimi Karşılaştırması

| TürkçePython       | Python         |
|--------------------|----------------|
| `yaz(...)`         | `print(...)`   |
| `gir(...)`         | `input(...)`   |
| `eğer`             | `if`           |
| `yoksa_eğer`       | `elif`         |
| `yoksa`            | `else`         |
| `için ... içinde`  | `for ... in`   |
| `döngü`            | `while`        |
| `tanım`            | `def`          |
| `sınıf`            | `class`        |
| `dön`              | `return`       |
| `dene`             | `try`          |
| `yakala`           | `except`       |
| `ve`               | `and`          |
| `veya`             | `or`           |
| `değil`            | `not`          |
| `Doğru`            | `True`         |
| `Yanlış`           | `False`        |
| `Hiç`              | `None`         |
| `kes`              | `break`        |
| `devam`            | `continue`     |
| `içe_aktar`        | `import`       |
| `uzunluk(...)`     | `len(...)`     |
| `aralık(...)`      | `range(...)`   |
| `liste(...)`       | `list(...)`    |
| `sözlük(...)`      | `dict(...)`    |
| `tam_sayı(...)`    | `int(...)`     |
| `ondalık(...)`     | `float(...)`   |
| `metin(...)`       | `str(...)`     |
| `toplam(...)`      | `sum(...)`     |
| `en_büyük(...)`    | `max(...)`     |
| `en_küçük(...)`    | `min(...)`     |

---

## Örnek Programlar

### Merhaba Dünya
```
yaz("Merhaba, Dünya!")
```

### FizzBuzz
```
için i içinde aralık(1, 101):
    eğer i % 15 == 0:
        yaz("FizzBuzz")
    yoksa_eğer i % 3 == 0:
        yaz("Fizz")
    yoksa_eğer i % 5 == 0:
        yaz("Buzz")
    yoksa:
        yaz(i)
```

### Kullanıcıdan girdi alma
```
isim = gir("Adınız nedir? ")
yaz("Merhaba,", isim)
```

---

## Nasıl Çalışır?

TürkçePython bir **transpiler** (kaynak-kaynak derleyici) + **yorumlayıcı** ikilisidir:

1. `.tr` dosyasını okur
2. Türkçe anahtar kelimeleri Python karşılıklarıyla değiştirir  
   (string literalleri ve yorumları değiştirmez)
3. Elde edilen Python kodunu `compile()` + `exec()` ile çalıştırır

---

## Notlar

- Girintileme (indentation) Python ile aynıdır — 4 boşluk önerilir.
- Türkçe karakterler (ğ, ş, ç, ı, ö, ü) hem değişken adlarında hem anahtar kelimelerde kullanılabilir.
- ASCII alternatifler de desteklenir: `eger`, `dongu`, `tanim`, vb.
- `import` modülleri Python'un kendi modülleridir — `import matematik` yerine `import math` yazılır.
