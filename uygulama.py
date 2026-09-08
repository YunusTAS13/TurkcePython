"""
TürkçePython IDE — Masaüstü Uygulama
Gereksinim: Python 3.8+ (tkinter dahil gelir)
Exe yapmak için: pyinstaller --onefile --windowed uygulama.py
"""
 
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font as tkfont
import sys
import io
import os
import threading
import contextlib
 
# ── Yorumlayıcıyı içe aktar (aynı klasörde turkce.py olmalı) ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from turkce import turkce_python_cevir, turkce_hata_formatla
 
# ────────────────────────────────────────────────────────────
# RENK TEMASı
# ────────────────────────────────────────────────────────────
TEMA = {
    "arkaplan":       "#1e1e2e",
    "panel":          "#181825",
    "kenarlık":       "#313244",
    "metin":          "#cdd6f4",
    "metin_soluk":    "#6c7086",
    "vurgu":          "#89b4fa",
    "vurgu2":         "#cba6f7",
    "başarı":         "#a6e3a1",
    "hata":           "#f38ba8",
    "uyarı":          "#fab387",
    "satır_no":       "#45475a",
    "satır_aktif":    "#313244",
    "seçim":          "#45475a",
    "anahtar":        "#cba6f7",   # mor  — anahtar kelimeler
    "fonksiyon":      "#89b4fa",   # mavi — fonksiyon adları
    "string":         "#a6e3a1",   # yeşil
    "yorum":          "#6c7086",   # gri
    "sayı":           "#fab387",   # turuncu
    "menü_bg":        "#181825",
    "menü_fg":        "#cdd6f4",
    "menü_aktif_bg":  "#313244",
    "durum_bg":       "#11111b",
}
 
TURKCE_ANAHTAR = [
    "eğer","eger","yoksa_eğer","yoksa_eger","yoksa","döngü","dongu",
    "için","icin","içinde","icinde","kes","devam","geç","gec",
    "tanım","tanim","sınıf","sinif","dön","don","ve","veya","değil","degil",
    "Doğru","Dogru","Yanlış","Yanlis","Hiç","Hic",
    "dene","yakala","sonunda","yükselt","yukselt",
    "içe_aktar","ice_aktar","den","olarak","sil","iddia","global",
    "yerel_dışı","yerel_disi","verim","ile","bekle","lambda",
]
 
TURKCE_FONK = [
    "yaz","gir","uzunluk","tip","tam_sayı","tam_sayi","ondalık","ondalik",
    "metin","liste","demet","küme","kume","sözlük","sozluk","aralık","aralik",
    "sıralı","sirali","tersine","mutlak","yuvarlak","en_büyük","en_buyuk",
    "en_küçük","en_kucuk","toplam","hepsi","herhangi","numaralandır",
    "numaralandir","eşleştir","eslesdir","harita","filtre","açık","acik",
    "ikili","sekizli","onaltılı","onaltili","karakter","kod_noktası","yardım",
    "kimlik","nesne","bool","bayt","derle","değerlendır","degerlendir",
    "çalıştır","calistir","biçimlendir","bicimlendir","nitelik_al",
    "nitelik_var","nitelik_sil","nitelik_koy","hash","girdi","sonraki",
]
 
VARSAYILAN_KOD = '''# TürkçePython'a hoş geldin!
# Aşağıdaki kodu çalıştırmak için F5'e bas veya Çalıştır butonuna tıkla.
 
tanım faktöriyel(n):
    eğer n <= 1:
        dön 1
    dön n * faktöriyel(n - 1)
 
yaz("── Faktöriyel Hesabı ──")
için i içinde aralık(1, 8):
    yaz(metin(i) + "! =", faktöriyel(i))
 
yaz("")
yaz("── Çift Sayılar ──")
çiftler = [x için x içinde aralık(1, 21) eğer x % 2 == 0]
yaz(çiftler)
'''
 
# ────────────────────────────────────────────────────────────
# SÖZDIZIMI RENKLENDIR
# ────────────────────────────────────────────────────────────
import re as _re
 
def renklendır(text_widget):
    """Tüm metni yeniden renklendir."""
    for tag in ("anahtar","fonksiyon","string","yorum","sayı"):
        text_widget.tag_remove(tag, "1.0", tk.END)
 
    kod = text_widget.get("1.0", tk.END)
    satirlar = kod.split("\n")
 
    for s_no, satir in enumerate(satirlar, start=1):
        lno = f"{s_no}."
 
        # Yorum
        m = _re.search(r'#.*$', satir)
        if m:
            text_widget.tag_add("yorum", f"{lno}{m.start()}", f"{lno}{m.end()}")
 
        # String
        for m in _re.finditer(r'(""".*?"""|\'\'\'.*?\'\'\'|"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\')', satir):
            text_widget.tag_add("string", f"{lno}{m.start()}", f"{lno}{m.end()}")
 
        # Sayı
        for m in _re.finditer(r'\b\d+\.?\d*\b', satir):
            text_widget.tag_add("sayı", f"{lno}{m.start()}", f"{lno}{m.end()}")
 
        # Anahtar kelimeler
        for kw in TURKCE_ANAHTAR:
            for m in _re.finditer(rf'\b{_re.escape(kw)}\b', satir):
                text_widget.tag_add("anahtar", f"{lno}{m.start()}", f"{lno}{m.end()}")
 
        # Fonksiyonlar
        for fn in TURKCE_FONK:
            for m in _re.finditer(rf'\b{_re.escape(fn)}\b', satir):
                text_widget.tag_add("fonksiyon", f"{lno}{m.start()}", f"{lno}{m.end()}")
 
 
# ────────────────────────────────────────────────────────────
# ANA UYGULAMA
# ────────────────────────────────────────────────────────────
class TurkcePythonIDE(tk.Tk):
 
    def __init__(self):
        super().__init__()
 
        self.title("TürkçePython IDE")
        self.geometry("1200x750")
        self.minsize(700, 450)
        self.configure(bg=TEMA["arkaplan"])
 
        # Durum değişkenleri
        self.mevcut_dosya = None
        self.degistirildi = False
        self.satir_no_goster = tk.BooleanVar(value=True)
        self.font_boyutu = tk.IntVar(value=14)
        self.calistiriliyor = False
 
        # Ayarlar
        self.kod_font = tkfont.Font(family="Consolas", size=14)
        self.ui_font  = tkfont.Font(family="Segoe UI",  size=10)
 
        self._pencere_ayarla()
        self._menu_olustur()
        self._arayuz_olustur()
        self._kisayollar()
        self._renk_etiketleri()
        self.kod_alani.insert("1.0", VARSAYILAN_KOD)
        self._renklendır()
        self._satir_guncelle()
        self.protocol("WM_DELETE_WINDOW", self._çıkış)
 
    # ── Pencere ──────────────────────────────
    def _pencere_ayarla(self):
        self.resizable(True, True)
        try:
            self.state("zoomed")       # Windows tam ekran
        except Exception:
            try:
                self.attributes("-zoomed", True)  # Linux
            except Exception:
                pass
 
    # ── Menü ─────────────────────────────────
    def _menu_olustur(self):
        menubar = tk.Menu(self,
            bg=TEMA["menü_bg"], fg=TEMA["menü_fg"],
            activebackground=TEMA["menü_aktif_bg"],
            activeforeground=TEMA["vurgu"],
            relief="flat", bd=0)
        self.configure(menu=menubar)
 
        # Dosya
        dosya_m = tk.Menu(menubar, tearoff=0,
            bg=TEMA["menü_bg"], fg=TEMA["menü_fg"],
            activebackground=TEMA["menü_aktif_bg"],
            activeforeground=TEMA["vurgu"])
        menubar.add_cascade(label="Dosya", menu=dosya_m)
        dosya_m.add_command(label="Yeni                    Ctrl+N", command=self._yeni)
        dosya_m.add_command(label="Aç...                   Ctrl+O", command=self._aç)
        dosya_m.add_separator()
        dosya_m.add_command(label="Kaydet                  Ctrl+S", command=self._kaydet)
        dosya_m.add_command(label="Farklı Kaydet...   Ctrl+Shift+S", command=self._farklı_kaydet)
        dosya_m.add_separator()
        dosya_m.add_command(label="Çıkış                   Alt+F4", command=self._çıkış)
 
        # Düzenle
        duzenle_m = tk.Menu(menubar, tearoff=0,
            bg=TEMA["menü_bg"], fg=TEMA["menü_fg"],
            activebackground=TEMA["menü_aktif_bg"],
            activeforeground=TEMA["vurgu"])
        menubar.add_cascade(label="Düzenle", menu=duzenle_m)
        duzenle_m.add_command(label="Geri Al          Ctrl+Z", command=lambda: self.kod_alani.edit_undo())
        duzenle_m.add_command(label="Yeniden Yap      Ctrl+Y", command=lambda: self.kod_alani.edit_redo())
        duzenle_m.add_separator()
        duzenle_m.add_command(label="Kes              Ctrl+X", command=lambda: self.kod_alani.event_generate("<<Cut>>"))
        duzenle_m.add_command(label="Kopyala          Ctrl+C", command=lambda: self.kod_alani.event_generate("<<Copy>>"))
        duzenle_m.add_command(label="Yapıştır         Ctrl+V", command=lambda: self.kod_alani.event_generate("<<Paste>>"))
        duzenle_m.add_separator()
        duzenle_m.add_command(label="Tümünü Seç       Ctrl+A", command=lambda: self.kod_alani.tag_add("sel","1.0",tk.END))
 
        # Çalıştır
        calistir_m = tk.Menu(menubar, tearoff=0,
            bg=TEMA["menü_bg"], fg=TEMA["menü_fg"],
            activebackground=TEMA["menü_aktif_bg"],
            activeforeground=TEMA["vurgu"])
        menubar.add_cascade(label="Çalıştır", menu=calistir_m)
        calistir_m.add_command(label="Çalıştır           F5", command=self._çalıştır)
        calistir_m.add_command(label="Çıktıyı Temizle    F6", command=self._çıktı_temizle)
 
        # Görünüm / Ayarlar
        ayarlar_m = tk.Menu(menubar, tearoff=0,
            bg=TEMA["menü_bg"], fg=TEMA["menü_fg"],
            activebackground=TEMA["menü_aktif_bg"],
            activeforeground=TEMA["vurgu"])
        menubar.add_cascade(label="Ayarlar", menu=ayarlar_m)
 
        # Font boyutu alt menüsü
        font_m = tk.Menu(ayarlar_m, tearoff=0,
            bg=TEMA["menü_bg"], fg=TEMA["menü_fg"],
            activebackground=TEMA["menü_aktif_bg"],
            activeforeground=TEMA["vurgu"])
        ayarlar_m.add_cascade(label="Font Boyutu", menu=font_m)
        for boyut in [10, 11, 12, 13, 14, 15, 16, 18, 20, 24]:
            font_m.add_radiobutton(
                label=f"  {boyut}px",
                variable=self.font_boyutu,
                value=boyut,
                command=self._font_değiştir)
 
        ayarlar_m.add_separator()
        ayarlar_m.add_checkbutton(
            label="Satır Numaraları",
            variable=self.satir_no_goster,
            command=self._satir_no_toggle)
 
        # Hakkında
        hakkında_m = tk.Menu(menubar, tearoff=0,
            bg=TEMA["menü_bg"], fg=TEMA["menü_fg"],
            activebackground=TEMA["menü_aktif_bg"],
            activeforeground=TEMA["vurgu"])
        menubar.add_cascade(label="Hakkında", menu=hakkında_m)
        hakkında_m.add_command(label="TürkçePython Hakkında", command=self._hakkında)
        hakkında_m.add_command(label="Dil Referansı",         command=self._referans)
 
    # ── Arayüz ───────────────────────────────
    def _arayuz_olustur(self):
        # Üst araç çubuğu
        araç = tk.Frame(self, bg=TEMA["panel"], height=44, bd=0)
        araç.pack(fill="x", side="top")
        araç.pack_propagate(False)
 
        def araç_btn(parent, etiket, komut, renk=None):
            r = renk or TEMA["vurgu"]
            b = tk.Button(parent, text=etiket, command=komut,
                bg=TEMA["panel"], fg=r,
                activebackground=TEMA["kenarlık"], activeforeground=r,
                relief="flat", bd=0, padx=14, pady=8,
                cursor="hand2", font=self.ui_font)
            b.pack(side="left", padx=2, pady=4)
            return b
 
        araç_btn(araç, "▶  Çalıştır (F5)", self._çalıştır, TEMA["başarı"])
        araç_btn(araç, "✕  Temizle   (F6)", self._çıktı_temizle, TEMA["metin_soluk"])
 
        tk.Frame(araç, bg=TEMA["kenarlık"], width=1).pack(side="left", fill="y", padx=8, pady=6)
 
        araç_btn(araç, "📄 Yeni",    self._yeni)
        araç_btn(araç, "📂 Aç",      self._aç)
        araç_btn(araç, "💾 Kaydet",  self._kaydet)
 
        # Dosya adı etiketi
        self.dosya_etiketi = tk.Label(araç, text="— yeni dosya —",
            bg=TEMA["panel"], fg=TEMA["metin_soluk"], font=self.ui_font)
        self.dosya_etiketi.pack(side="left", padx=16)
 
        # Ana bölücü (editör | çıktı)
        self.ana_paned = tk.PanedWindow(self, orient="vertical",
            bg=TEMA["kenarlık"], sashwidth=4,
            sashrelief="flat", bd=0)
        self.ana_paned.pack(fill="both", expand=True)
 
        # ── Editör paneli ──
        editor_frame = tk.Frame(self.ana_paned, bg=TEMA["arkaplan"])
        self.ana_paned.add(editor_frame, minsize=150)
 
        # Satır numaraları
        self.satir_çerçeve = tk.Frame(editor_frame, bg=TEMA["panel"], width=52)
        self.satir_çerçeve.pack(side="left", fill="y")
 
        self.satir_canvas = tk.Canvas(self.satir_çerçeve,
            bg=TEMA["panel"], highlightthickness=0, width=52)
        self.satir_canvas.pack(fill="both", expand=True)
 
        # Kod alanı
        kod_frame = tk.Frame(editor_frame, bg=TEMA["arkaplan"])
        kod_frame.pack(side="left", fill="both", expand=True)
 
        self.kod_kaydırma_y = ttk.Scrollbar(kod_frame, orient="vertical")
        self.kod_kaydırma_y.pack(side="right", fill="y")
        self.kod_kaydırma_x = ttk.Scrollbar(kod_frame, orient="horizontal")
        self.kod_kaydırma_x.pack(side="bottom", fill="x")
 
        self.kod_alani = tk.Text(kod_frame,
            bg=TEMA["arkaplan"], fg=TEMA["metin"],
            insertbackground=TEMA["vurgu"],
            selectbackground=TEMA["seçim"], selectforeground=TEMA["metin"],
            font=self.kod_font,
            relief="flat", bd=0,
            padx=12, pady=8,
            wrap="none",
            undo=True,
            yscrollcommand=self._kod_kaydır_y,
            xscrollcommand=self.kod_kaydırma_x.set,
            tabs=("1c",),
            spacing3=2,
        )
        self.kod_alani.pack(fill="both", expand=True)
        self.kod_kaydırma_y.config(command=self._kod_kaydır_komut)
        self.kod_kaydırma_x.config(command=self.kod_alani.xview)
 
        # ── Çıktı paneli ──
        çıktı_frame = tk.Frame(self.ana_paned, bg=TEMA["panel"])
        self.ana_paned.add(çıktı_frame, minsize=80)
 
        başlık = tk.Frame(çıktı_frame, bg=TEMA["panel"], height=30)
        başlık.pack(fill="x")
        başlık.pack_propagate(False)
        tk.Label(başlık, text="  Çıktı", bg=TEMA["panel"],
            fg=TEMA["metin_soluk"], font=self.ui_font).pack(side="left", pady=4)
 
        self.çıktı_kaydırma = ttk.Scrollbar(çıktı_frame, orient="vertical")
        self.çıktı_kaydırma.pack(side="right", fill="y")
 
        self.çıktı_alani = tk.Text(çıktı_frame,
            bg=TEMA["panel"], fg=TEMA["metin"],
            font=tkfont.Font(family="Consolas", size=13),
            relief="flat", bd=0,
            padx=12, pady=8,
            state="disabled",
            yscrollcommand=self.çıktı_kaydırma.set,
            wrap="word",
        )
        self.çıktı_alani.pack(fill="both", expand=True)
        self.çıktı_kaydırma.config(command=self.çıktı_alani.yview)
 
        self.çıktı_alani.tag_config("hata",   foreground=TEMA["hata"])
        self.çıktı_alani.tag_config("başarı", foreground=TEMA["başarı"])
        self.çıktı_alani.tag_config("bilgi",  foreground=TEMA["metin_soluk"])
 
        # Durum çubuğu
        durum = tk.Frame(self, bg=TEMA["durum_bg"], height=24)
        durum.pack(fill="x", side="bottom")
        durum.pack_propagate(False)
        self.durum_sol = tk.Label(durum, text="Hazır",
            bg=TEMA["durum_bg"], fg=TEMA["metin_soluk"],
            font=tkfont.Font(family="Segoe UI", size=9))
        self.durum_sol.pack(side="left", padx=10)
        self.durum_sağ = tk.Label(durum, text="Satır: 1  Sütun: 1",
            bg=TEMA["durum_bg"], fg=TEMA["metin_soluk"],
            font=tkfont.Font(family="Segoe UI", size=9))
        self.durum_sağ.pack(side="right", padx=10)
 
        # Olaylar
        self.kod_alani.bind("<<Modified>>", self._kod_değişti)
        self.kod_alani.bind("<KeyRelease>", self._tuş_bırakıldı)
        self.kod_alani.bind("<ButtonRelease>", self._imleç_guncelle)
        self.kod_alani.bind("<Tab>", self._tab_bas)
 
        # Bölücüyü başlat
        self.update_idletasks()
        h = self.winfo_height()
        self.ana_paned.sash_place(0, 0, max(100, int(h * 0.62)))
 
    # ── Renk etiketleri ──────────────────────
    def _renk_etiketleri(self):
        self.kod_alani.tag_config("anahtar",  foreground=TEMA["anahtar"])
        self.kod_alani.tag_config("fonksiyon",foreground=TEMA["fonksiyon"])
        self.kod_alani.tag_config("string",   foreground=TEMA["string"])
        self.kod_alani.tag_config("yorum",    foreground=TEMA["yorum"])
        self.kod_alani.tag_config("sayı",     foreground=TEMA["sayı"])
 
    # ── Kısayollar ───────────────────────────
    def _kisayollar(self):
        self.bind("<F5>",            lambda e: self._çalıştır())
        self.bind("<F6>",            lambda e: self._çıktı_temizle())
        self.bind("<Control-n>",     lambda e: self._yeni())
        self.bind("<Control-o>",     lambda e: self._aç())
        self.bind("<Control-s>",     lambda e: self._kaydet())
        self.bind("<Control-S>",     lambda e: self._farklı_kaydet())
        self.bind("<Control-z>",     lambda e: self.kod_alani.edit_undo())
        self.bind("<Control-y>",     lambda e: self.kod_alani.edit_redo())
 
    # ── Kaydırma senkronizasyonu ─────────────
    def _kod_kaydır_y(self, *args):
        self.kod_kaydırma_y.set(*args)
        self._satir_güncelle_canvas()
 
    def _kod_kaydır_komut(self, *args):
        self.kod_alani.yview(*args)
        self._satir_güncelle_canvas()
 
    # ── Satır numaraları ─────────────────────
    def _satir_guncelle(self):
        self._satir_güncelle_canvas()
 
    def _satir_güncelle_canvas(self):
        if not self.satir_no_goster.get():
            return
        c = self.satir_canvas
        c.delete("all")
        c.configure(bg=TEMA["panel"])
 
        i = self.kod_alani.index("@0,0")
        while True:
            dline = self.kod_alani.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            satir_no = int(str(i).split(".")[0])
            c.create_text(44, y + 2,
                text=str(satir_no),
                anchor="ne",
                fill=TEMA["satır_no"],
                font=self.kod_font)
            i = self.kod_alani.index(f"{i}+1line")
            if i == self.kod_alani.index(f"{i}-1line"):
                break
 
    def _satir_no_toggle(self):
        if self.satir_no_goster.get():
            self.satir_çerçeve.pack(side="left", fill="y", before=self.kod_alani.master)
            self._satir_güncelle_canvas()
        else:
            self.satir_çerçeve.pack_forget()
 
    # ── Olaylar ──────────────────────────────
    def _tab_bas(self, event):
        self.kod_alani.insert("insert", "    ")
        return "break"
 
    def _kod_değişti(self, event=None):
        if self.kod_alani.edit_modified():
            self.degistirildi = True
            self._başlık_güncelle()
            self.kod_alani.edit_modified(False)
 
    def _tuş_bırakıldı(self, event=None):
        self._renklendır()
        self._satir_güncelle_canvas()
        self._imleç_guncelle()
 
    def _imleç_guncelle(self, event=None):
        pos = self.kod_alani.index("insert")
        s, c = pos.split(".")
        self.durum_sağ.config(text=f"Satır: {s}  Sütun: {int(c)+1}")
 
    def _renklendır(self):
        try:
            renklendır(self.kod_alani)
        except Exception:
            pass
 
    # ── Başlık ───────────────────────────────
    def _başlık_güncelle(self):
        ad = os.path.basename(self.mevcut_dosya) if self.mevcut_dosya else "yeni dosya"
        değ = " •" if self.degistirildi else ""
        self.title(f"TürkçePython IDE — {ad}{değ}")
        self.dosya_etiketi.config(
            text=f"{'— ' + ad + ' —'}" if not self.mevcut_dosya else ad)
 
    # ── Dosya işlemleri ──────────────────────
    def _yeni(self):
        if not self._kaydet_onayla():
            return
        self.kod_alani.delete("1.0", tk.END)
        self.mevcut_dosya = None
        self.degistirildi = False
        self._başlık_güncelle()
        self.durum_sol.config(text="Yeni dosya oluşturuldu")
 
    def _aç(self):
        if not self._kaydet_onayla():
            return
        yol = filedialog.askopenfilename(
            title="Dosya Aç",
            filetypes=[("TürkçePython", "*.tr"), ("Tüm Dosyalar", "*.*")])
        if not yol:
            return
        try:
            with open(yol, encoding="utf-8") as f:
                içerik = f.read()
            self.kod_alani.delete("1.0", tk.END)
            self.kod_alani.insert("1.0", içerik)
            self.mevcut_dosya = yol
            self.degistirildi = False
            self._başlık_güncelle()
            self._renklendır()
            self.durum_sol.config(text=f"Açıldı: {yol}")
        except Exception as h:
            messagebox.showerror("Hata", str(h))
 
    def _kaydet(self):
        if self.mevcut_dosya:
            self._dosyaya_yaz(self.mevcut_dosya)
        else:
            self._farklı_kaydet()
 
    def _farklı_kaydet(self):
        yol = filedialog.asksaveasfilename(
            title="Farklı Kaydet",
            defaultextension=".tr",
            filetypes=[("TürkçePython", "*.tr"), ("Tüm Dosyalar", "*.*")])
        if yol:
            self._dosyaya_yaz(yol)
            self.mevcut_dosya = yol
            self._başlık_güncelle()
 
    def _dosyaya_yaz(self, yol):
        try:
            with open(yol, "w", encoding="utf-8") as f:
                f.write(self.kod_alani.get("1.0", tk.END))
            self.degistirildi = False
            self._başlık_güncelle()
            self.durum_sol.config(text=f"Kaydedildi: {yol}")
        except Exception as h:
            messagebox.showerror("Hata", str(h))
 
    def _kaydet_onayla(self) -> bool:
        if not self.degistirildi:
            return True
        yanıt = messagebox.askyesnocancel(
            "Kaydedilmemiş Değişiklikler",
            "Değişiklikleri kaydetmek ister misin?")
        if yanıt is None:
            return False
        if yanıt:
            self._kaydet()
        return True
 
    # ── Çalıştır ─────────────────────────────
    def _çalıştır(self):
        if self.calistiriliyor:
            return
        kaynak = self.kod_alani.get("1.0", tk.END)
        self._çıktı_temizle()
        self.durum_sol.config(text="Çalıştırılıyor...")
        self.calistiriliyor = True
        t = threading.Thread(target=self._calistir_thread, args=(kaynak,), daemon=True)
        t.start()
 
    def _calistir_thread(self, kaynak):
        çıktı_buf = io.StringIO()
        hata_var = False
        try:
            python_kod = turkce_python_cevir(kaynak)
            global_değ = {"__name__": "__main__"}
 
            with contextlib.redirect_stdout(çıktı_buf), \
                 contextlib.redirect_stderr(çıktı_buf):
                exec(compile(python_kod, "<editör>", "exec"), global_değ)
 
        except SyntaxError as h:
            hata_var = True
            çıktı_buf.write(f"\n💥 SözDizimHatası: {h.msg}\n   Satır {h.lineno}: {h.text or ''}\n")
        except BaseException as h:
            hata_var = True
            çıktı_buf.write(turkce_hata_formatla(h))
 
        sonuç = çıktı_buf.getvalue()
        self.after(0, self._çıktı_göster, sonuç, hata_var)
 
    def _çıktı_göster(self, metin, hata_var):
        self.çıktı_alani.config(state="normal")
        if metin:
            tag = "hata" if hata_var else "başarı"
            self.çıktı_alani.insert(tk.END, metin, tag)
        else:
            self.çıktı_alani.insert(tk.END, "(çıktı yok)\n", "bilgi")
        self.çıktı_alani.config(state="disabled")
        self.çıktı_alani.see(tk.END)
        self.calistiriliyor = False
        self.durum_sol.config(text="✓ Tamamlandı" if not hata_var else "✕ Hata oluştu")
 
    def _çıktı_temizle(self):
        self.çıktı_alani.config(state="normal")
        self.çıktı_alani.delete("1.0", tk.END)
        self.çıktı_alani.config(state="disabled")
        self.durum_sol.config(text="Çıktı temizlendi")
 
    # ── Font ─────────────────────────────────
    def _font_değiştir(self):
        boyut = self.font_boyutu.get()
        self.kod_font.config(size=boyut)
        self._satir_güncelle_canvas()
 
    # ── Hakkında ─────────────────────────────
    def _hakkında(self):
        pencere = tk.Toplevel(self)
        pencere.title("Hakkında")
        pencere.geometry("420x300")
        pencere.configure(bg=TEMA["arkaplan"])
        pencere.resizable(False, False)
        pencere.transient(self)
        pencere.grab_set()
 
        tk.Label(pencere, text="TürkçePython IDE",
            bg=TEMA["arkaplan"], fg=TEMA["vurgu"],
            font=tkfont.Font(family="Segoe UI", size=18, weight="bold")).pack(pady=(30,4))
        tk.Label(pencere, text="Sürüm 1.1",
            bg=TEMA["arkaplan"], fg=TEMA["metin_soluk"],
            font=tkfont.Font(family="Segoe UI", size=11)).pack()
        tk.Label(pencere, text="\nTamamen Türkçe sözdizimli\nbir programlama dili ve editörü.\n\nPython 3.8+ üzerinde çalışır.",
            bg=TEMA["arkaplan"], fg=TEMA["metin"],
            font=tkfont.Font(family="Segoe UI", size=11),
            justify="center").pack(pady=10)
        tk.Button(pencere, text="Kapat",
            command=pencere.destroy,
            bg=TEMA["kenarlık"], fg=TEMA["metin"],
            relief="flat", padx=24, pady=6,
            cursor="hand2").pack(pady=10)
 
    def _referans(self):
        pencere = tk.Toplevel(self)
        pencere.title("Dil Referansı")
        pencere.geometry("560x520")
        pencere.configure(bg=TEMA["arkaplan"])
        pencere.transient(self)
 
        tk.Label(pencere, text="TürkçePython — Sözdizimi Referansı",
            bg=TEMA["arkaplan"], fg=TEMA["vurgu"],
            font=tkfont.Font(family="Segoe UI", size=13, weight="bold")).pack(pady=(16,8))
 
        frame = tk.Frame(pencere, bg=TEMA["arkaplan"])
        frame.pack(fill="both", expand=True, padx=16)
 
        sb = ttk.Scrollbar(frame)
        sb.pack(side="right", fill="y")
 
        tablo = tk.Text(frame, bg=TEMA["panel"], fg=TEMA["metin"],
            font=tkfont.Font(family="Consolas", size=11),
            relief="flat", bd=0, padx=12, pady=8,
            yscrollcommand=sb.set, state="normal")
        tablo.pack(fill="both", expand=True)
        sb.config(command=tablo.yview)
 
        tablo.tag_config("başlık", foreground=TEMA["vurgu2"], font=tkfont.Font(family="Consolas", size=11, weight="bold"))
        tablo.tag_config("tr",     foreground=TEMA["anahtar"])
        tablo.tag_config("py",     foreground=TEMA["metin_soluk"])
 
        satırlar = [
            ("── Kontrol Akışı ──────────────────────────────", "başlık"),
            ("  eğer / eger             →  if", None),
            ("  yoksa_eğer              →  elif", None),
            ("  yoksa                   →  else", None),
            ("  için … içinde           →  for … in", None),
            ("  döngü                   →  while", None),
            ("  kes                     →  break", None),
            ("  devam                   →  continue", None),
            ("", None),
            ("── Fonksiyon & Sınıf ──────────────────────────", "başlık"),
            ("  tanım                   →  def", None),
            ("  sınıf                   →  class", None),
            ("  dön                     →  return", None),
            ("  lambda                  →  lambda", None),
            ("", None),
            ("── Değerler ───────────────────────────────────", "başlık"),
            ("  Doğru / Dogru           →  True", None),
            ("  Yanlış / Yanlis         →  False", None),
            ("  Hiç / Hic               →  None", None),
            ("", None),
            ("── Mantık ─────────────────────────────────────", "başlık"),
            ("  ve                      →  and", None),
            ("  veya                    →  or", None),
            ("  değil                   →  not", None),
            ("", None),
            ("── Hata Yönetimi ──────────────────────────────", "başlık"),
            ("  dene                    →  try", None),
            ("  yakala                  →  except", None),
            ("  sonunda                 →  finally", None),
            ("  yükselt                 →  raise", None),
            ("", None),
            ("── Yerleşik Fonksiyonlar ──────────────────────", "başlık"),
            ("  yaz(...)                →  print(...)", None),
            ("  gir(...)                →  input(...)", None),
            ("  uzunluk(...)            →  len(...)", None),
            ("  aralık(...)             →  range(...)", None),
            ("  tam_sayı(...)           →  int(...)", None),
            ("  ondalık(...)            →  float(...)", None),
            ("  metin(...)              →  str(...)", None),
            ("  liste(...)              →  list(...)", None),
            ("  sözlük(...)             →  dict(...)", None),
            ("  toplam(...)             →  sum(...)", None),
            ("  en_büyük(...)           →  max(...)", None),
            ("  en_küçük(...)           →  min(...)", None),
            ("  harita(...)             →  map(...)", None),
            ("  filtre(...)             →  filter(...)", None),
        ]
 
        for metin_str, tag in satırlar:
            if tag:
                tablo.insert(tk.END, metin_str + "\n", tag)
            else:
                tablo.insert(tk.END, metin_str + "\n")
 
        tablo.config(state="disabled")
 
    # ── Çıkış ────────────────────────────────
    def _çıkış(self):
        if self._kaydet_onayla():
            self.destroy()
 
 
# ────────────────────────────────────────────────────────────
# GİRİŞ NOKTASI
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uygulama = TurkcePythonIDE()
    uygulama.mainloop()
