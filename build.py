import math, random, urllib.parse, pathlib

W = pathlib.Path(__file__).resolve().parent          # source/ folder (holds template.html)
OUT = W.parent                                          # project root: writes index.html here


def r1(x):
    return f'{x:.1f}'.rstrip('0').rstrip('.')


# ---------- cusped (multifoil) Rajput arch ----------
def arch(w=200, h=140, n=5, R=0.64, rf=1.0):
    R *= w
    cosA = w / (2 * R) - 1
    thL = math.degrees(math.acos(cosA))
    sp = R * math.sin(math.radians(thL))
    L = []
    for i in range(n + 1):
        th = math.radians(180 - (180 - thL) * i / n)
        L.append((R + R * math.cos(th), sp - R * math.sin(th)))
    phiA = 180 - thL
    Rt = []
    for i in range(1, n + 1):
        ph = math.radians(phiA - phiA * i / n)
        Rt.append((w - R + R * math.cos(ph), sp - R * math.sin(ph)))
    pts = L + Rt
    d = f'M0,{h} L{r1(pts[0][0])},{r1(pts[0][1])}'
    for a, b in zip(pts, pts[1:]):
        c = math.dist(a, b)
        r = c * rf
        d += f' A{r1(r)},{r1(r)} 0 0 1 {r1(b[0])},{r1(b[1])}'
    d += f' L{w},{h}'
    return d, sp


def arch_svg():
    w, h, P = 200, 140, 12
    line, sp = arch(w, h)
    inner, _ = arch(w - 22, h - 11)
    vb = f'{-P} {-P} {w + 2 * P} {h + P}'
    svg = (
        f'<svg class="arch-svg" viewBox="{vb}" aria-hidden="true" focusable="false">'
        f'<path class="a-fill" d="{line} L{w},{h + 2} L0,{h + 2} Z"/>'
        f'<path class="a-in" transform="translate(11 11)" d="{inner}"/>'
        f'<path class="a-line" d="{line}"/>'
        f'</svg>'
        '<svg class="arch-ic" viewBox="-50 -50 100 100" aria-hidden="true"><use href="#rosette" x="-50" y="-50" width="100" height="100"/></svg>'
    )
    return svg, P / (w + 2 * P) * 100


ARCH_SVG, ARCH_PAD = arch_svg()


# ---------- skyline ----------
def merlons(x0, x1, y, w=8, gap=7, h=9):
    d, x = '', x0
    while x + w <= x1:
        d += f'M{x},{y} V{y - h + 3} L{r1(x + w / 2)},{y - h - 3} L{x + w},{y - h + 3} V{y} Z '
        x += w + gap
    return d


def dome(cx, by, r, h):
    return (
        f'M{r1(cx - r)},{by} C{r1(cx - r)},{r1(by - h * .55)} {r1(cx - r * .25)},{r1(by - h * .75)} {cx},{r1(by - h * 1.2)} '
        f'C{r1(cx + r * .25)},{r1(by - h * .75)} {r1(cx + r)},{r1(by - h * .55)} {r1(cx + r)},{by} Z '
        f'M{cx - 1},{r1(by - h * 1.2)} h2 v-{r1(h * .35)} h-2 Z '
    )


def chhatri(cx, by, w, h):
    d = f'M{r1(cx - w / 2 - 3)},{by - h} h{w + 6} v4 h-{w + 6} Z '
    for k in range(4):
        x = cx - w / 2 + k * (w - 3) / 3
        d += f'M{r1(x)},{by} v-{h} h3 v{h} Z '
    d += dome(cx, by - h, w / 2 - 2, w * .55)
    return d


def sky_far():
    d = 'M0,128 H520 V220 H0 Z ' + merlons(0, 520, 128, 8, 8, 9)
    for x in (60, 260, 460):
        d += f'M{x - 18},100 h36 V128 h-36 Z ' + dome(x, 100, 18, 22)
    for x in (150, 370):
        d += chhatri(x, 128, 26, 18)
    return d


def sky_mid():
    d = 'M110,118 H410 V220 H110 Z ' + merlons(110, 410, 118, 8, 8, 9)
    d += chhatri(260, 118, 34, 24)
    for x in (140, 380):
        d += chhatri(x, 118, 20, 14)
    for x in (96, 424):
        d += f'M{x - 16},84 h32 V220 h-32 Z ' + merlons(x - 16, x + 16, 84, 6, 4, 7) + dome(x, 74, 15, 20)
    return d


def sky_windows():
    out = ''
    wd, _ = arch(14, 26, 1, 0.62, 1.4)
    big, _ = arch(44, 64, 1, 0.62, 1.5)
    lit = {(0, 1), (0, 3), (0, 4), (1, 0), (1, 2), (1, 5), (0, 5)}
    for row, y in enumerate((130, 168)):
        for k in range(6):
            x = 134 + k * 46
            cls = 'win on' if (row, k) in lit else 'win'
            out += f'<path class="{cls}" transform="translate({x} {y})" d="{wd} Z"/>'
    out += f'<path class="win gate" transform="translate(238 156)" d="{big} Z"/>'
    return out


def sky_near():
    return 'M0,196 H520 V220 H0 Z ' + merlons(0, 520, 196, 10, 10, 10)


def stars():
    random.seed(11)
    s = ''
    for i in range(46):
        x, y = random.randint(8, 512), random.randint(8, 330)
        r = random.choice((0.8, 1, 1.2, 1.6))
        tw = ' class="tw"' if i % 5 == 0 else ''
        delay = f' style="animation-delay:{random.random() * 4:.1f}s"' if tw else ''
        s += f'<circle cx="{x}" cy="{y}" r="{r}"{tw}{delay}/>'
    return s


# ---------- symbols ----------
def rosette(petal='currentColor'):
    s = ''
    for k in range(8):
        s += f'<ellipse cx="0" cy="-30" rx="10" ry="22" transform="rotate({k * 45})" fill="{petal}"/>'
    for k in range(8):
        s += f'<ellipse cx="0" cy="-18" rx="6" ry="13" transform="rotate({k * 45 + 22.5})" fill="{petal}" opacity=".7"/>'
    return s


def peacock():
    feather = (
        '<g id="pf">'
        '<path d="M120,176 C104,140 102,92 120,50 C138,92 136,140 120,176Z" fill="#2E9380" stroke="#E8C66F" stroke-width="1.3"/>'
        '<path d="M120,176 V70" stroke="#E8C66F" stroke-width="1" opacity=".7"/>'
        '<ellipse cx="120" cy="76" rx="12" ry="17" fill="#E0B13F"/>'
        '<ellipse cx="120" cy="76" rx="8.2" ry="12.5" fill="#1C5F57"/>'
        '<ellipse cx="120" cy="77" rx="4.6" ry="7" fill="#15305F"/>'
        '<circle cx="118.6" cy="74" r="1.6" fill="#F3E6C8"/>'
        '</g>'
    )
    s = f'<symbol id="peacock" viewBox="0 0 240 256"><defs>{feather}</defs>'
    for a in range(-75, 76, 15):
        s += f'<use href="#pf" transform="rotate({a} 120 176)"/>'
    for a in range(-67, 68, 15):
        s += (f'<use href="#pf" transform="rotate({a} 120 176) translate(120 176) scale(.72) translate(-120 -176)" '
              f'opacity=".95"/>')
    s += (
        '<g stroke="#E8C66F" stroke-width="1.2" stroke-linejoin="round">'
        '<path d="M106,196 C102,170 113,162 114,146 L126,146 C127,162 138,170 134,196Z" fill="#17406E"/>'
        '<ellipse cx="120" cy="208" rx="25" ry="32" fill="#1B5C8A"/>'
        '<ellipse cx="120" cy="140" rx="9.5" ry="10.5" fill="#17406E"/>'
        '</g>'
        '<path d="M111,128 L120,142 L129,128Z" fill="#E8C66F" transform="translate(0 4) scale(1 .7) translate(0 58)" opacity="0"/>'
        '<path d="M115.5,143 L120,153 L124.5,143Z" fill="#E8C66F"/>'
        '<ellipse cx="120" cy="139" rx="5.5" ry="4" fill="#F3E6C8" opacity=".9"/>'
        '<circle cx="117.5" cy="137.5" r="1.4" fill="#15305F"/><circle cx="122.5" cy="137.5" r="1.4" fill="#15305F"/>'
        '<path d="M120,131 V108 M116,132 L110,112 M124,132 L130,112" stroke="#E8C66F" stroke-width="1.4" fill="none"/>'
        '<circle cx="120" cy="106" r="2.6" fill="#E8C66F"/><circle cx="109.5" cy="110" r="2.3" fill="#E8C66F"/>'
        '<circle cx="130.5" cy="110" r="2.3" fill="#E8C66F"/>'
        '<path d="M106,200 C112,222 128,222 134,200" fill="none" stroke="#E8C66F" stroke-width="1" opacity=".7"/>'
        '<path d="M112,160 C118,170 122,170 128,160" fill="none" stroke="#E8C66F" stroke-width="1" opacity=".7"/>'
        '<path d="M110,238 L108,252 M130,238 L132,252 M102,252 H114 M126,252 H138" stroke="#E8C66F" stroke-width="2.6" stroke-linecap="round"/>'
        '</symbol>'
    )
    return s


def elephant():
    hem = ''.join(
        f'A10.2,10.2 0 0 1 {r1(214 - 20.33 * (i + 1))},142 ' for i in range(6)
    )
    tassels = ''.join(f'<circle cx="{r1(214 - 20.33 * (i + .5))}" cy="154" r="2.6" fill="#E8C66F"/>' for i in range(6))
    diamonds = ''.join(
        f'<path d="M{r1(104 + i * 18)},96 l5,6 l-5,6 l-5,-6Z" fill="#E8C66F"/>' for i in range(6)
    )
    return (
        '<symbol id="elephant" viewBox="0 -12 332 252">'
        '<ellipse cx="160" cy="226" rx="120" ry="6" fill="#000" opacity=".25"/>'
        # far legs
        '<rect x="86" y="148" width="26" height="76" rx="9" fill="#9C7A49"/>'
        '<rect x="208" y="154" width="26" height="70" rx="9" fill="#9C7A49"/>'
        # tail
        '<path d="M64,108 C46,118 42,144 50,166" fill="none" stroke="#B8955F" stroke-width="5" stroke-linecap="round"/>'
        '<ellipse cx="50" cy="168" rx="4.5" ry="8" fill="#6B4A28"/>'
        # body
        '<path d="M62,118 C58,78 96,58 150,58 C206,58 238,72 244,108 C248,140 238,174 212,174 L88,174 C70,170 64,146 62,118Z" fill="#C9A878"/>'
        # near legs
        '<rect x="64" y="150" width="29" height="76" rx="10" fill="#C9A878"/>'
        '<rect x="184" y="156" width="29" height="70" rx="10" fill="#C9A878"/>'
        '<rect x="63" y="200" width="31" height="7" rx="2" fill="#E8C66F"/><rect x="183" y="200" width="31" height="7" rx="2" fill="#E8C66F"/>'
        '<g fill="#F3E6C8"><ellipse cx="72" cy="221" rx="3.2" ry="4"/><ellipse cx="86" cy="221" rx="3.2" ry="4"/>'
        '<ellipse cx="192" cy="221" rx="3.2" ry="4"/><ellipse cx="206" cy="221" rx="3.2" ry="4"/></g>'
        # head
        '<path d="M226,86 C230,56 262,42 288,54 C310,66 314,100 304,126 C300,136 294,140 288,142 L254,148 C236,142 224,114 226,86Z" fill="#C9A878"/>'
        # trunk
        '<path d="M262,124 C268,152 270,184 262,208 C258,220 272,228 284,216 C300,198 302,164 302,130 Z" fill="#C9A878"/>'
        '<g fill="none" stroke="#9C7A49" stroke-width="2" stroke-linecap="round">'
        '<path d="M268,142 Q282,146 296,142"/><path d="M268,158 Q282,162 298,157"/><path d="M267,174 Q281,178 297,172"/><path d="M265,190 Q278,194 292,188"/></g>'
        # tusk
        '<path d="M294,130 C310,138 322,148 324,164 C312,156 300,150 290,142Z" fill="#F3E6C8"/>'
        # ear
        '<path d="M236,70 C216,66 200,86 204,108 C208,130 228,134 238,120 C244,102 246,82 236,70Z" fill="#B8955F"/>'
        '<path d="M232,80 C220,82 214,98 218,112" fill="none" stroke="#8A6A3C" stroke-width="2"/>'
        # forehead plate
        '<path d="M240,60 C258,48 282,52 292,68 C286,88 274,100 264,114 C250,100 238,82 240,60Z" fill="#E8C66F" stroke="#6B1424" stroke-width="1.5"/>'
        '<path d="M262,64 l8,12 l-8,12 l-8,-12Z" fill="#6B1424"/><circle cx="262" cy="76" r="3" fill="#E8C66F"/>'
        '<circle cx="280" cy="86" r="4" fill="#C9A878" stroke="#6B1424" stroke-width="1.2"/>'
        # eye
        '<circle cx="284" cy="92" r="3.2" fill="#2B0B10"/>'
        # neck chain + bell
        '<path d="M226,120 C232,150 252,160 276,150" fill="none" stroke="#E8C66F" stroke-width="3"/>'
        '<circle cx="244" cy="157" r="6" fill="#E8C66F" stroke="#6B1424" stroke-width="1.2"/>'
        # jhool (blanket)
        f'<path d="M92,62 H214 V142 {hem}Z" fill="#6B1424" stroke="#E8C66F" stroke-width="3" stroke-linejoin="round"/>'
        '<path d="M100,72 H206" stroke="#E8C66F" stroke-width="1.5"/>'
        f'{diamonds}'
        '<g transform="translate(153 124) scale(.2)" fill="#E8C66F">'
        '<ellipse cx="0" cy="-30" rx="10" ry="22"/><ellipse cx="0" cy="-30" rx="10" ry="22" transform="rotate(45)"/>'
        '<ellipse cx="0" cy="-30" rx="10" ry="22" transform="rotate(-45)"/><ellipse cx="0" cy="-30" rx="10" ry="22" transform="rotate(90)"/>'
        '<ellipse cx="0" cy="-30" rx="10" ry="22" transform="rotate(-90)"/></g>'
        f'{tassels}'
        # howdah
        '<rect x="120" y="42" width="68" height="18" rx="3" fill="#E8C66F" stroke="#6B1424" stroke-width="1.5"/>'
        '<path d="M126,42 V22 M148,42 V22 M170,42 V22 M182,42 V22" stroke="#E8C66F" stroke-width="3"/>'
        '<path d="M116,24 C128,2 180,2 192,24Z" fill="#E8C66F" stroke="#6B1424" stroke-width="1.5"/>'
        '<path d="M126,24 q7,9 14,0 q7,9 14,0 q7,9 14,0 q7,9 14,0" fill="#6B1424"/>'
        '<path d="M154,3 V-4" stroke="#E8C66F" stroke-width="2"/><circle cx="154" cy="-6" r="3" fill="#E8C66F"/>'
        '</symbol>'
    )


SPRITE = (
    '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
    # lotus
    '<symbol id="lotus" viewBox="0 0 60 32">'
    '<path d="M30 2 C37 9 37 21 30 29 C23 21 23 9 30 2Z" fill="currentColor"/>'
    '<path d="M30 29 C24 28 14 24 11 12 C19 13 26 19 30 29Z" fill="currentColor" opacity=".85"/>'
    '<path d="M30 29 C36 28 46 24 49 12 C41 13 34 19 30 29Z" fill="currentColor" opacity=".85"/>'
    '<path d="M30 29 C20 30 8 27 2 18 C12 16 22 20 30 29Z" fill="currentColor" opacity=".6"/>'
    '<path d="M30 29 C40 30 52 27 58 18 C48 16 38 20 30 29Z" fill="currentColor" opacity=".6"/>'
    '</symbol>'
    # rosette
    f'<symbol id="rosette" viewBox="-50 -50 100 100">{rosette()}<circle r="8" fill="currentColor"/></symbol>'
    # icons
    '<symbol id="i-haldi" viewBox="0 0 64 64">'
    '<path d="M9 38 H55 C55 51 45 59 32 59 C19 59 9 51 9 38Z" fill="currentColor"/>'
    '<path d="M17 38 C19 29 45 29 47 38Z" fill="currentColor"/>'
    '<path d="M17 47 H47" class="k" stroke-width="2" fill="none"/><path d="M21 52 H43" class="k" stroke-width="2" fill="none"/>'
    '<g transform="translate(32 17) scale(.19)" fill="currentColor">' + rosette() + '</g>'
    '<circle cx="32" cy="17" r="2.6" class="kf"/>'
    '</symbol>'
    '<symbol id="i-mehandi" viewBox="0 0 64 64">'
    '<path d="M24 8 C40 12 46 30 38 44 C32 54 18 56 10 48 C19 49 24 42 24 34 C24 25 18 19 24 8Z" fill="currentColor"/>'
    '<path d="M28 22 C35 26 36 36 31 42" class="k" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '<circle cx="30" cy="30" r="1.8" class="kf"/><circle cx="25" cy="39" r="1.6" class="kf"/>'
    '<path d="M46 30 C54 34 56 46 50 54 C46 59 38 59 34 56 C40 56 44 51 44 45 C44 40 42 35 46 30Z" fill="currentColor" opacity=".8"/>'
    '</symbol>'
    '<symbol id="i-safa" viewBox="0 0 64 64">'
    '<path d="M7 46 C3 24 17 8 33 8 C50 8 62 24 57 46 C48 54 16 54 7 46Z" fill="currentColor"/>'
    '<path d="M9 40 C22 50 46 50 56 38 M7 32 C20 42 46 42 58 30 M11 24 C22 33 42 33 52 22" class="k" stroke-width="2.4" fill="none"/>'
    '<path d="M12 46 C22 52 44 52 52 46 L52 52 C44 58 20 58 12 52Z" fill="currentColor"/>'
    '<circle cx="24" cy="30" r="6.5" class="kf"/><circle cx="24" cy="30" r="3.2" fill="currentColor"/>'
    '<path d="M24 24 C25 14 31 8 40 6 C36 11 33 16 29 25" fill="currentColor"/>'
    '</symbol>'
    '<symbol id="i-kalash" viewBox="0 0 64 64">'
    '<path d="M20 28 C10 38 14 56 32 58 C50 56 54 38 44 28Z" fill="currentColor"/>'
    '<rect x="22" y="22" width="20" height="7" rx="3" fill="currentColor"/>'
    '<path d="M16 38 C24 42 40 42 48 38" class="k" stroke-width="2" fill="none"/>'
    '<path d="M22 49 l5 -5 l5 5 l5 -5 l5 5" class="k" stroke-width="2" fill="none"/>'
    '<path d="M32 22 C22 18 14 12 12 6 C22 6 30 12 32 22Z" fill="currentColor" opacity=".85"/>'
    '<path d="M32 22 C42 18 50 12 52 6 C42 6 34 12 32 22Z" fill="currentColor" opacity=".85"/>'
    '<ellipse cx="32" cy="12" rx="7.5" ry="9" fill="currentColor"/>'
    '<path d="M32 4 V20" class="k" stroke-width="1.5" fill="none"/>'
    '</symbol>'
    # peacock, elephant
    + peacock() + elephant() +
    '</defs></svg>'
)


def dataurl(svg):
    return 'data:image/svg+xml,' + urllib.parse.quote(svg, safe="/:=',()._- ")


KANGURA = lambda c: dataurl(f"<svg xmlns='http://www.w3.org/2000/svg' width='28' height='14' viewBox='0 0 28 14'><path d='M0 14 V9 Q14 -6 28 9 V14Z' fill='{c}'/></svg>")
DOOR = dataurl(
    "<svg xmlns='http://www.w3.org/2000/svg' width='72' height='72' viewBox='0 0 72 72'>"
    "<path d='M36 4 L68 36 L36 68 L4 36Z' fill='none' stroke='#E8C66F' stroke-opacity='.28' stroke-width='1.2'/>"
    "<path d='M36 14 L58 36 L36 58 L14 36Z' fill='none' stroke='#E8C66F' stroke-opacity='.16' stroke-width='1'/>"
    "<circle cx='36' cy='36' r='5.5' fill='#C8962E'/><circle cx='34.6' cy='34.6' r='2.2' fill='#F6E3A1'/>"
    "<circle cx='0' cy='0' r='2.2' fill='#C8962E'/><circle cx='72' cy='0' r='2.2' fill='#C8962E'/>"
    "<circle cx='0' cy='72' r='2.2' fill='#C8962E'/><circle cx='72' cy='72' r='2.2' fill='#C8962E'/></svg>"
)
JAALI = dataurl(
    "<svg xmlns='http://www.w3.org/2000/svg' width='56' height='56' viewBox='0 0 56 56'>"
    "<path d='M28 0 L56 28 L28 56 L0 28Z' fill='none' stroke='#E8C66F' stroke-opacity='.13' stroke-width='1'/>"
    "<circle cx='28' cy='28' r='2.4' fill='#E8C66F' fill-opacity='.18'/></svg>"
)
BLOCK = dataurl(
    "<svg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 64 64'>"
    "<g fill='#B9915A' fill-opacity='.2'>"
    "<ellipse cx='16' cy='16' rx='2.4' ry='5.5'/><ellipse cx='16' cy='16' rx='2.4' ry='5.5' transform='rotate(90 16 16)'/>"
    "<ellipse cx='16' cy='16' rx='2.2' ry='5' transform='rotate(45 16 16)'/><ellipse cx='16' cy='16' rx='2.2' ry='5' transform='rotate(-45 16 16)'/>"
    "<circle cx='48' cy='48' r='2.6'/><circle cx='48' cy='32' r='1.2'/><circle cx='32' cy='48' r='1.2'/></g></svg>"
)

cal_text = (
    "Haldi (बान): Wed 9 Dec, 4:15 PM. Mehandi (रातीजोगा): Thu 10 Dec. Nikasi (निकासी): Fri 11 Dec, 12:15 PM. "
    "Baraat Prasthan (बारात प्रस्थान): Fri 11 Dec, 3:15 PM, from Pundalsar to Sattasar. Wedding day: Fri 11 Dec 2026."
)
CAL = ('https://calendar.google.com/calendar/render?action=TEMPLATE&text='
       + urllib.parse.quote('Rajendra (Rishi) & Chanda Wedding') + '&dates=20261209/20261212&details=' + urllib.parse.quote(cal_text))

rep = {
    '@@SPRITE@@': SPRITE,
    '@@ARCH@@': ARCH_SVG,
    '@@ARCHPAD@@': f'{ARCH_PAD:.2f}%',
    '@@STARS@@': stars(),
    '@@SKYFAR@@': sky_far(),
    '@@SKYMID@@': sky_mid(),
    '@@SKYWIN@@': sky_windows(),
    '@@SKYNEAR@@': sky_near(),
    '@@KAN_IVORY@@': KANGURA('#F3E6C8'),
    '@@KAN_MAROON@@': KANGURA('#3A0912'),
    '@@DOOR@@': DOOR,
    '@@JAALI@@': JAALI,
    '@@BLOCK@@': BLOCK,
    '@@CAL@@': CAL.replace('&', '&amp;'),
}

html = (W / 'template.html').read_text(encoding='utf-8')
for k, v in rep.items():
    html = html.replace(k, v)
left = [t for t in rep if False]
assert '@@' not in html, [l for l in html.split('@@')[1:2]]
(OUT / 'index.html').write_text(html, encoding='utf-8')
print('ok', len(html))
