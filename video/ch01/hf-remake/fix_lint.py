from pathlib import Path
import re
COMP = Path(__file__).resolve().parent / "compositions"
for p in COMP.glob("b0*.html"):
    t = p.read_text(encoding="utf-8")
    t = t.replace(".scene{", "#root{")
    t = t.replace('class="scene clip"', 'class="clip"')
    def fix_hv(m):
        hid, at, hd, fname = m.group(1), m.group(2), m.group(3), m.group(4)
        return (
            f'<div id="hv-{hid}" class="huashu-wrap" style="position:absolute;inset:0;pointer-events:none">'
            f'<div class="huashu-in" id="hv-{hid}-in" style="width:100%;height:100%;opacity:0">'
            f'<video id="vid-{hid}" class="clip" src="../assets/huashu/{fname}" muted playsinline '
            f'data-start="{at}" data-duration="{hd}" data-has-audio="false" '
            f'style="width:100%;height:100%;object-fit:cover"></video>'
            f'</div></div>'
        )
    t2 = re.sub(
        r'<div id="hv-([^"]+)" class="clip huashu-wrap" data-start="([^"]+)" data-duration="([^"]+)"[^>]*>\s*'
        r'<div class="huashu-in" id="hv-\1-in">\s*'
        r'<video src="../assets/huashu/([^"]+)"[^>]*>\s*</video>\s*</div>\s*</div>',
        fix_hv,
        t,
        flags=re.S,
    )
    print(p.name, "huashu-fixed" if t2 != t else "NO-MATCH")
    p.write_text(t2, encoding="utf-8")
print("OK")
