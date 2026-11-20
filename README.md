# ela-text-tools

ComfyUI için iki metin birleştirme node'u. Prompt parçalarını üst üste yazıp tek
string olarak çıkarmak için.

| Node | Kategori | Girdi tipi |
|---|---|---|
| **Ela Text Concat** | `ela/text` | tek node içinde N tane multiline metin kutusu (1-12) |
| **Ela Text Join (autogrow)** | `ela/text` | açıldıkça büyüyen socket'ler (2-32), `COMFY_AUTOGROW_V3` |

## Kurulum

**ComfyUI-Manager** → *Install Custom Nodes* → *Install via Git URL*:

```
https://github.com/cemcakirlar/ela-text-tools
```

Kurulumdan sonra ComfyUI'yı yeniden başlat. Bağımlılık yok, `pip install`
gerekmez; ComfyUI core ile gelen `torch` ve `comfy_api` yeterli.

Elle kurmak istersen:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/cemcakirlar/ela-text-tools
```

Klasör adı `ela-text-tools` kalmalı (JS uzantısı bu ad üzerinden servis edilir).

## Ela Text Concat

Tek node içinde çok satırlı kutular; `+ satir` / `- satir` ile satır ekle/çıkar.

- `count` — kaç satır kullanılacak (1-12)
- `separator` — satır arasına konacak ayırıcı (varsayılan `, `)
- `text_1 … text_12` — multiline metin kutuları

Boş satırlar atlanır, her satırın baştaki/sondaki boşluğu kırpılır, sıra
yukarıdan aşağı. Kutulara string bağlarsan widget yerine bağlantı kullanılır.

## Ela Text Join (autogrow)

ComfyUI'nin yeni v3 node API'si ve `COMFY_AUTOGROW_V3` girdi tipini kullanır.

- `text0, text1, …` — bağlantı ekledikçe kendiliğinden büyür (2-32 slot, ilk ikisi zorunlu)
- `delimiter` — ayırıcı (varsayılan `, `)
- `skip_empty` — boş slotları atla / koru
- `trim` — baş-son boşlukları kırp / olduğu gibi bırak

Slotlar socket: her birine bir `Text (Multiline)` primitifi bağlanır. Sınırsız
sayıda parça gerektiğinde bunu, sabit ve kutu görünümlü bir node gerektiğinde
`Ela Text Concat`'i kullan.

Sıralama numeriktir: `text2` her zaman `text10`'dan önce gelir.

## Geliştirme

Kod `custom_nodes/ela-text-tools` içinde. JS değişikliği için tarayıcıda
`Ctrl+Shift+R` yeterli; Python değişikliği için ComfyUI'yı yeniden başlat.

```
ela-text-tools/
├─ __init__.py            # Ela Text Concat + mapping + dev reload route
├─ auto_text.py           # Ela Text Join (autogrow), v3 API
├─ js/ela_text_tools.js   # slot göster/gizle, +/- butonları
├─ LICENSE
└─ README.md
```

`__init__.py` içinde `POST /ela_text_tools/reload` route'u var; sadece
geliştirme sırasında işe yarar, üretimde zararsız.

## Lisans

MIT
