"""
TürkçePython - Tamamen Türkçe sözdizimli bir programlama dili yorumlayıcısı.
Python 3.12+ ile çalışır.
Kullanım: python turkce.py dosya.tr
"""

import sys
import re
import math
import os

# ──────────────────────────────────────────────
# ANAHTAR KELİME DÖNÜŞÜM TABLOSU
# ──────────────────────────────────────────────

KELIMELER = {
    # Kontrol akışı
    "eğer":       "if",
    "eger":       "if",
    "yoksa_eğer": "elif",
    "yoksa_eger": "elif",
    "yoksa":      "else",
    "döngü":      "while",
    "dongu":      "while",
    "için":       "for",
    "icin":       "for",
    "içinde":     "in",
    "icinde":     "in",
    "kes":        "break",
    "devam":      "continue",
    "geç":        "pass",
    "gec":        "pass",

    # Fonksiyon / sınıf
    "tanım":      "def",
    "tanim":      "def",
    "sınıf":      "class",
    "sinif":      "class",
    "dön":        "return",
    "don":        "return",
    "lambda":     "lambda",

    # Mantık operatörleri
    "ve":         "and",
    "veya":       "or",
    "değil":      "not",
    "degil":      "not",

    # Değerler
    "Doğru":      "True",
    "Dogru":      "True",
    "Yanlış":     "False",
    "Yanlis":     "False",
    "Hiç":        "None",
    "Hic":        "None",

    # İstisna yönetimi
    "dene":       "try",
    "yakala":     "except",
    "sonunda":    "finally",
    "yükselt":    "raise",
    "yukselt":    "raise",

    # Modül
    "içe_aktar":  "import",
    "ice_aktar":  "import",
    "den":        "from",
    "olarak":     "as",

    # Diğer
    "sil":        "del",
    "iddia":      "assert",
    "global":     "global",
    "yerel_dışı": "nonlocal",
    "yerel_disi": "nonlocal",
    "verim":      "yield",
    "ile":        "with",
    "async":      "async",
    "bekle":      "await",
}

# Türkçe yerleşik fonksiyonlar
TURKCE_FONKSIYONLAR = {
    "yaz":          "print",
    "gir":          "input",
    "uzunluk":      "len",
    "tip":          "type",
    "tam_sayı":     "int",
    "tam_sayi":     "int",
    "ondalık":      "float",
    "ondalik":      "float",
    "metin":        "str",
    "liste":        "list",
    "demet":        "tuple",
    "küme":         "set",
    "kume":         "set",
    "sözlük":       "dict",
    "sozluk":       "dict",
    "aralık":       "range",
    "aralik":       "range",
    "sıralı":       "sorted",
    "sirali":       "sorted",
    "tersine":      "reversed",
    "mutlak":       "abs",
    "yuvarlak":     "round",
    "en_büyük":     "max",
    "en_buyuk":     "max",
    "en_küçük":     "min",
    "en_kucuk":     "min",
    "toplam":       "sum",
    "hepsi":        "all",
    "herhangi":     "any",
    "numaralandır": "enumerate",
    "numaralandir": "enumerate",
    "eşleştir":     "zip",
    "eslesdir":     "zip",
    "harita":       "map",
    "filtre":       "filter",
    "açık":         "open",
    "acik":         "open",
    "baskı":        "print",
    "baski":        "print",
    "ikili":        "bin",
    "sekizli":      "oct",
    "onaltılı":     "hex",
    "onaltili":     "hex",
    "karakter":     "chr",
    "kod_noktası":  "ord",
    "kod_noktasi":  "ord",
    "çağrılabilir": "callable",
    "cagrilabilir": "callable",
    "yardım":       "help",
    "yardim":       "help",
    "dir":          "dir",
    "kimlik":       "id",
    "isinstance":   "isinstance",
    "issubclass":   "issubclass",
    "super":        "super",
    "nesne":        "object",
    "bool":         "bool",
    "bayt":         "bytes",
    "bytearray":    "bytearray",
    "dondur":       "frozenset",
    "bellek_görüntüsü": "memoryview",
    "bellek_goruntusu": "memoryview",
    "derle":        "compile",
    "değerlendır":  "eval",
    "degerlendir":  "eval",
    "çalıştır":     "exec",
    "calistir":     "exec",
    "biçimlendir":  "format",
    "bicimlendir":  "format",
    "nitelik_al":   "getattr",
    "nitelik_var":  "hasattr",
    "nitelik_sil":  "delattr",
    "nitelik_koy":  "setattr",
    "hash":         "hash",
    "girdi":        "input",
    "iter":         "iter",
    "sonraki":      "next",
    "vars":         "vars",
    "globals":      "globals",
    "locals":       "locals",
}

# ──────────────────────────────────────────────
# DÖNÜŞTÜRÜCÜ
# ──────────────────────────────────────────────

def turkce_python_cevir(kaynak: str) -> str:
    """Türkçe kaynak kodunu geçerli Python koduna dönüştürür."""
    satirlar = kaynak.splitlines()
    sonuc = []

    for satir in satirlar:
        donusturulmus = satir_cevir(satir)
        sonuc.append(donusturulmus)

    return "\n".join(sonuc)


def satir_cevir(satir: str) -> str:
    """Tek bir satırı dönüştürür (string literalleri koruyarak)."""
    parcalar = string_parcala(satir)
    yeni_parcalar = []

    for parca, string_mi in parcalar:
        if string_mi:
            yeni_parcalar.append(parca)
        else:
            yeni_parcalar.append(token_cevir(parca))

    return "".join(yeni_parcalar)


def string_parcala(satir: str):
    """
    Satırı string içi / string dışı parçalara böler.
    Döner: [(metin, string_mi), ...]
    """
    sonuc = []
    i = 0
    n = len(satir)

    while i < n:
        # Üçlü tırnak kontrolü
        for uclu in ('"""', "'''"):
            if satir[i:i+3] == uclu:
                bitis = satir.find(uclu, i + 3)
                if bitis == -1:
                    bitis = n - 3
                bitis += 3
                sonuc.append((satir[i:bitis], True))
                i = bitis
                break
        else:
            # Tekli tırnak
            if satir[i] in ('"', "'"):
                tirnak = satir[i]
                j = i + 1
                while j < n:
                    if satir[j] == '\\':
                        j += 2
                        continue
                    if satir[j] == tirnak:
                        j += 1
                        break
                    j += 1
                sonuc.append((satir[i:j], True))
                i = j
            # Yorum satırı # → geri kalanı olduğu gibi koy
            elif satir[i] == '#':
                sonuc.append((satir[i:], False))
                break
            else:
                # Normal metin biriktir
                if sonuc and not sonuc[-1][1]:
                    sonuc[-1] = (sonuc[-1][0] + satir[i], False)
                else:
                    sonuc.append((satir[i], False))
                i += 1
                continue
    return sonuc


def token_cevir(metin: str) -> str:
    """String olmayan metin parçasındaki Türkçe token'ları Python karşılığıyla değiştirir."""

    # Önce fonksiyon adlarını değiştir (parantez öncesi)
    for tr, py in sorted(TURKCE_FONKSIYONLAR.items(), key=lambda x: -len(x[0])):
        metin = re.sub(rf'\b{re.escape(tr)}\b', py, metin)

    # Sonra anahtar kelimeleri değiştir
    for tr, py in sorted(KELIMELER.items(), key=lambda x: -len(x[0])):
        metin = re.sub(rf'\b{re.escape(tr)}\b', py, metin)

    return metin


# ──────────────────────────────────────────────
# TÜRKÇE HATA MESAJLARI
# ──────────────────────────────────────────────

HATA_MESAJLARI = {
    "SyntaxError":        "SözDizimHatası",
    "NameError":          "İsimHatası",
    "TypeError":          "TipHatası",
    "ValueError":         "DeğerHatası",
    "IndexError":         "DizinHatası",
    "KeyError":           "AnahtarHatası",
    "AttributeError":     "NitelikHatası",
    "ImportError":        "İçeAktarmaHatası",
    "FileNotFoundError":  "DosyaBulunamadıHatası",
    "ZeroDivisionError":  "SıfıraBölmeHatası",
    "RecursionError":     "ÖzyinelemeHatası",
    "MemoryError":        "BellekHatası",
    "OverflowError":      "TaşmaHatası",
    "RuntimeError":       "ÇalışmaZamanıHatası",
    "StopIteration":      "YinelemeDurdu",
    "PermissionError":    "İzinHatası",
    "OSError":            "İşletimSistemiHatası",
    "NotImplementedError":"UygulanmadıHatası",
    "Exception":          "İstisna",
}

def turkce_hata_formatla(hata: Exception) -> str:
    tip_adi = type(hata).__name__
    tr_ad = HATA_MESAJLARI.get(tip_adi, tip_adi)
    return f"\n💥 {tr_ad}: {hata}\n"


# ──────────────────────────────────────────────
# ÇALIŞTIRICISI
# ──────────────────────────────────────────────

def dosya_calistir(dosya_yolu: str):
    """Türkçe .tr dosyasını okuyup çalıştırır."""
    try:
        with open(dosya_yolu, "r", encoding="utf-8") as f:
            kaynak = f.read()
    except FileNotFoundError:
        print(f"💥 DosyaBulunamadıHatası: '{dosya_yolu}' bulunamadı.")
        sys.exit(1)

    python_kod = turkce_python_cevir(kaynak)

    # Hata ayıklama: TURKCE_DEBUG=1 ile dönüştürülmüş kodu göster
    if os.environ.get("TURKCE_DEBUG"):
        print("─── Dönüştürülmüş Python Kodu ───")
        for i, satir in enumerate(python_kod.splitlines(), 1):
            print(f"{i:4}: {satir}")
        print("─────────────────────────────────\n")

    try:
        kod_nesnesi = compile(python_kod, dosya_yolu, "exec")
        global_degiskenler = {
            "__name__": "__main__",
            "__file__": dosya_yolu,
        }
        exec(kod_nesnesi, global_degiskenler)
    except SyntaxError as h:
        print(f"\n💥 SözDizimHatası: {h.msg}")
        print(f"   Satır {h.lineno}: {h.text}")
        if os.environ.get("TURKCE_DEBUG"):
            raise
        sys.exit(1)
    except Exception as h:
        print(turkce_hata_formatla(h))
        if os.environ.get("TURKCE_DEBUG"):
            raise
        sys.exit(1)


def interaktif_mod():
    """REPL — satır satır Türkçe kod çalıştır."""
    print("TürkçePython 1.0  |  Python", sys.version.split()[0])
    print("Çıkmak için: çık() veya Ctrl+C\n")

    gecmis = []

    while True:
        try:
            satir = input(">>> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGüle güle!")
            break

        if satir.strip() in ("çık()", "cik()", "exit()", "quit()"):
            print("Güle güle!")
            break

        if not satir.strip():
            continue

        gecmis.append(satir)
        python_kod = turkce_python_cevir("\n".join(gecmis))

        try:
            kod = compile(python_kod, "<girdi>", "exec")
            exec(kod, {"__name__": "__main__"})
        except SyntaxError:
            # Belki çok satırlı bir blok — devam et
            try:
                devam = input("... ")
                gecmis.append(devam)
            except (EOFError, KeyboardInterrupt):
                gecmis = []
        except Exception as h:
            print(turkce_hata_formatla(h))
            gecmis = []


# ──────────────────────────────────────────────
# GİRİŞ NOKTASI
# ──────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        interaktif_mod()
    else:
        dosya_yolu = sys.argv[1]
        dosya_calistir(dosya_yolu)


if __name__ == "__main__":
    main()
