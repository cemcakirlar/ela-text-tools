"""Ela Text Join (autogrow) - ComfyUI v3 node, COMFY_AUTOGROW_V3 kullanir.

ElaTextConcat'ten farki:
  - slot sayisi sabit 12 degil, native autogrow (2..32), sinirsiz baglanti
  - slotlar socket: her birine Text (Multiline) primitifi baglanir
  - JS yok, backend her sey

Tek basina paket olarak da, ela_text_tools icinden de yuklenebilir.
"""

from comfy_api.latest import ComfyExtension, io

MAX_SLOTS = 32


def _slot_index(name):
    """text12 -> 12, text2 -> 2 (alfabetik siralamayi duzeltmek icin)."""
    digits = ""
    for ch in reversed(str(name)):
        if ch.isdigit():
            digits = ch + digits
        else:
            break
    return int(digits) if digits else 10 ** 6


class ElaTextJoinAuto(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        template = io.Autogrow.TemplatePrefix(
            input=io.String.Input("text"),
            prefix="text",
            min=2,
            max=MAX_SLOTS,
        )

        return io.Schema(
            node_id="ElaTextJoinAuto",
            display_name="Ela Text Join (autogrow)",
            category="ela/text",
            search_aliases=["concat", "join", "autogrow", "metin birlestir", "text join"],
            description=(
                "Autogrow metin slotlari: bagladikca yeni slot acilir. "
                "Bosluk birakilan slotlar atlanir, sira text0, text1, text2... seklinde."
            ),
            inputs=[
                io.Autogrow.Input(
                    "texts",
                    template=template,
                    tooltip="Her slota bir Text / string bagla. Kullanmadigin bos kalabilir.",
                ),
                io.String.Input(
                    "delimiter",
                    default=", ",
                    multiline=False,
                    tooltip="Parcalar arasina konacak ayirici.",
                ),
                io.Boolean.Input("skip_empty", default=True, label_on="atla", label_off="koru"),
                io.Boolean.Input("trim", default=True, label_on="kirp", label_off="oldugu gibi"),
            ],
            outputs=[
                io.String.Output(display_name="text"),
            ],
        )

    @classmethod
    def execute(
        cls,
        texts: io.Autogrow.Type = None,
        delimiter: str = ", ",
        skip_empty: bool = True,
        trim: bool = True,
    ) -> io.NodeOutput:
        values = texts or {}

        parts = []
        for name in sorted(values.keys(), key=_slot_index):
            value = values[name]
            if value is None:
                continue
            if not isinstance(value, str):
                value = str(value)
            if trim:
                value = value.strip()
            if skip_empty and not value:
                continue
            parts.append(value)

        return io.NodeOutput(str(delimiter).join(parts))


NODE_CLASS_MAPPINGS = {
    "ElaTextJoinAuto": ElaTextJoinAuto,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ElaTextJoinAuto": "Ela Text Join (autogrow)",
}


class ElaAutoTextExtension(ComfyExtension):
    async def get_node_list(self):
        return [ElaTextJoinAuto]


async def comfy_entrypoint():
    return ElaAutoTextExtension()
