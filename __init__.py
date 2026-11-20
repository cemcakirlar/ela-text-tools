"""Ela Text Tools - ComfyUI custom node pack (demo).

Node: Ela Text Concat
    N adet multiline metin satirini yukaridan asagiya birlestirip tek STRING verir.

Dosya duzeni:
    ela_text_tools/
        __init__.py      (bu dosya: node + mapping + reload route)
        js/
            ela_text_tools.js   (slot goster/gizle, + / - butonlari)
"""

MAX_SLOTS = 12

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
WEB_DIRECTORY = "./js"


class ElaTextConcat:
    """Yukaridan asagiya N satir metni birlestirir."""

    @classmethod
    def INPUT_TYPES(cls):
        required = {
            "count": (
                "INT",
                {
                    "default": 3,
                    "min": 1,
                    "max": MAX_SLOTS,
                    "step": 1,
                    "tooltip": "Kac metin satiri birlestirilecek (1 - %d)" % MAX_SLOTS,
                },
            ),
            "separator": (
                "STRING",
                {
                    "default": ", ",
                    "multiline": False,
                    "tooltip": "Satirlar arasina konacak ayirici. Bos birakirsan duz yapistirir.",
                },
            ),
        }

        optional = {}
        for i in range(1, MAX_SLOTS + 1):
            optional["text_%d" % i] = (
                "STRING",
                {
                    "multiline": True,
                    "default": "",
                    "dynamicPrompts": False,
                    "placeholder": "metin %d" % i,
                },
            )

        return {"required": required, "optional": optional}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "concat"
    CATEGORY = "ela/text"
    DESCRIPTION = "N tane multiline metni yukaridan asagiya birlestirip tek string dondurur."
    SEARCH_ALIASES = ["concat", "join text", "merge text", "metin birlestir"]

    def concat(self, count, separator="", **kwargs):
        try:
            limit = int(count)
        except (TypeError, ValueError):
            limit = MAX_SLOTS
        limit = max(1, min(MAX_SLOTS, limit))

        parts = []
        for i in range(1, limit + 1):
            value = kwargs.get("text_%d" % i, "")
            if value is None:
                continue
            if not isinstance(value, str):
                value = str(value)
            value = value.strip()
            if value:
                parts.append(value)

        return (str(separator).join(parts),)


NODE_CLASS_MAPPINGS = {"ElaTextConcat": ElaTextConcat}
NODE_DISPLAY_NAME_MAPPINGS = {"ElaTextConcat": "Ela Text Concat"}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
    "ElaTextConcat",
    "MAX_SLOTS",
]


# --- v3 autogrow node (ayri dosya; ElaTextConcat'e dokunmaz) -----------------
# auto_text.py COMFY_AUTOGROW_V3 kullanan v3 node'u tanimlar. Burada elle
# yukluyoruz cunku ComfyUI bir pakette NODE_CLASS_MAPPINGS gorunce v3
# comfy_entrypoint yoluna hic bakmiyor.
try:
    import importlib.util as _importlib_util
    import os as _os

    _auto_spec = _importlib_util.spec_from_file_location(
        "ela_text_tools_auto_text",
        _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "auto_text.py"),
    )
    if _auto_spec is not None and _auto_spec.loader is not None:
        _auto_module = _importlib_util.module_from_spec(_auto_spec)
        _auto_spec.loader.exec_module(_auto_module)
        NODE_CLASS_MAPPINGS.update(_auto_module.NODE_CLASS_MAPPINGS)
        NODE_DISPLAY_NAME_MAPPINGS.update(_auto_module.NODE_DISPLAY_NAME_MAPPINGS)
except Exception as _exc:
    print("[ela_text_tools] auto_text.py yuklenemedi: %s" % _exc)


# --- dev reload (opsiyonel) -------------------------------------------------
# POST /ela_text_tools/reload -> paketi yeniden yukler, node'lari tekrar kaydeder.
# Sadece gelistirme icin; uretimde zararsiz ama gereksiz.
# Not: importlib.reload() burada calismaz, cunku ComfyUI custom node modulunu
# sentetik bir isimle (tam dosya yolu) kaydediyor; find_spec o ismi bulamaz.
# Bu yuzden spec.loader.exec_module ile taze modul olusturuyoruz.
try:
    import importlib.util
    import sys

    from aiohttp import web
    from server import PromptServer

    def _ela_reload_pack():
        import nodes

        me = sys.modules[__name__]
        old_keys = set(getattr(me, "NODE_CLASS_MAPPINGS", {}) or {})
        fresh = importlib.util.module_from_spec(me.__spec__)
        me.__spec__.loader.exec_module(fresh)
        sys.modules[__name__] = fresh

        for key in old_keys:
            nodes.NODE_CLASS_MAPPINGS.pop(key, None)
            nodes.NODE_DISPLAY_NAME_MAPPINGS.pop(key, None)
        nodes.NODE_CLASS_MAPPINGS.update(fresh.NODE_CLASS_MAPPINGS)
        nodes.NODE_DISPLAY_NAME_MAPPINGS.update(fresh.NODE_DISPLAY_NAME_MAPPINGS)
        return sorted(fresh.NODE_CLASS_MAPPINGS)

    _server = PromptServer.instance
    if not getattr(_server, "_ela_text_tools_reload_route", False):
        _server._ela_text_tools_reload_route = True

        @_server.routes.post("/ela_text_tools/reload")
        async def _ela_text_tools_reload(request):
            return web.json_response({"ok": True, "nodes": _ela_reload_pack()})
except Exception as exc:  # route eklenemezse node yine de calissin
    print("[ela_text_tools] reload route eklenemedi: %s" % exc)
