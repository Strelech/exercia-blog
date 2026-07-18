#!/usr/bin/env python3
"""
Exercia — Carousel PNG Exporter
Usage:
  python3 export_carousel.py                         # contenu par défaut
  python3 export_carousel.py --content content.json  # contenu custom
  python3 export_carousel.py --out ./output          # dossier de sortie custom

Format JSON attendu (content.json) :
{
  "slide1": {
    "tag": "CRPE 2026 · MÉTHODE",
    "eyebrow": "Tu travailles dur. Pourtant…",
    "title": "Tu rates les mêmes questions depuis <span class='hook-accent'>3 mois.</span>",
    "sub": "Ce n'est pas un manque de travail. C'est une méthode inadaptée."
  },
  "slide2": { "tag": "ERREUR #1", "title": "Réviser <span class='ct-accent'>sans tester</span> sa mémoire active", "body": "..." },
  "slide3": { "tag": "ERREUR #2", "title": "...", "body": "..." },
  "slide4": { "tag": "ERREUR #3", "title": "...", "body": "..." },
  "slide5": { "cta_label": "Prêt à changer de méthode ?", "title": "Entraîne-toi sur les vraies questions du CRPE.", "btn": "Essayer gratuitement", "sub": "exercia.org · lien en bio" }
}

MAJ (juillet 2026) :
- slide 1 — eyebrow 24px → 34px, sub 30px → 40px (retour : sous-textes trop petits sur mobile)
- slide 1 — logo blanc 108×33 → 180×55 (aligné sur le logo de la slide 5)
"""

import json
import argparse
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# ── Defaults ──────────────────────────────────────────────────────────────────

DEFAULT_CONTENT = {
    "slide1": {
        "tag": "CRPE 2026 · MÉTHODE",
        "eyebrow": "Tu travailles dur. Pourtant…",
        "title": "Tu rates les mêmes questions depuis <span class='hook-accent'>3 mois.</span>",
        "sub": "Ce n'est pas un manque de travail. C'est une méthode inadaptée. Voilà comment corriger ça."
    },
    "slide2": {
        "tag": "ERREUR #1",
        "step": "01",
        "title": "Réviser <span class='ct-accent'>sans tester</span> sa mémoire active",
        "body": "Relire ses fiches donne l'illusion de maîtrise. Le cerveau reconnaît sans retenir. Seul le rappel actif consolide vraiment la mémoire."
    },
    "slide3": {
        "tag": "ERREUR #2",
        "step": "02",
        "title": "Ignorer les <span class='ct-accent'>annales</span> des 3 dernières années",
        "body": "Le jury réutilise les mêmes typologies de questions. Les annales révèlent exactement ce qui tombe."
    },
    "slide4": {
        "tag": "ERREUR #3",
        "step": "03",
        "title": "Bachoter <span class='ct-accent'>sans cibler</span> les notions tombables",
        "body": "Toutes les notions ne se valent pas au CRPE. Certaines reviennent chaque année, d'autres jamais."
    },
    "slide5": {
        "tag": "LA SOLUTION",
        "cta_label": "Prêt à changer de méthode ?",
        "title": "Entraîne-toi sur les vraies questions du CRPE.",
        "btn": "Essayer gratuitement",
        "sub": "exercia.org · lien en bio"
    }
}

# ── HTML template ─────────────────────────────────────────────────────────────

def build_html(content: dict) -> str:
    s = content
    s1 = s["slide1"]
    s2 = s["slide2"]
    s3 = s["slide3"]
    s4 = s["slide4"]
    s5 = s["slide5"]

    logo_white = """<svg width="180" height="55" viewBox="0 0 360 110" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="rW" x1="38" y1="14" x2="94" y2="96" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#FFFEF5"/><stop offset="55%" stop-color="#FFFFFF"/><stop offset="100%" stop-color="#EDF7F8"/></linearGradient></defs>
      <circle cx="70" cy="55" r="34" stroke="url(#rW)" stroke-width="10" stroke-linecap="round" fill="none" stroke-dasharray="180 60" stroke-dashoffset="18"/>
      <path d="M54 55.5L66 67.5L88 43" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <text x="120" y="70" font-family="Inter,sans-serif" font-size="52" font-weight="700" fill="#FFFFFF" letter-spacing="-0.5">Exercia</text>
    </svg>"""

    logo_dark = """<svg width="108" height="33" viewBox="0 0 360 110" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="rD" x1="38" y1="14" x2="94" y2="96" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#63C6A6"/><stop offset="55%" stop-color="#3B8BC6"/><stop offset="100%" stop-color="#2F5BDB"/></linearGradient></defs>
      <circle cx="70" cy="55" r="34" stroke="url(#rD)" stroke-width="10" stroke-linecap="round" fill="none" stroke-dasharray="180 60" stroke-dashoffset="18"/>
      <path d="M54 55.5L66 67.5L88 43" stroke="#3B8BC6" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <text x="120" y="70" font-family="Inter,sans-serif" font-size="52" font-weight="700" fill="#1B1B1B" letter-spacing="-0.5">Exercia</text>
    </svg>"""

    slides_html = f"""
    <!-- SLIDE 1 : Hook -->
    <div id="slide-1" class="slide" style="background:#0F838F; width:1080px; height:1080px; padding:88px 96px; display:flex; flex-direction:column; justify-content:space-between; position:absolute; top:0; left:0; font-family:'Inter',sans-serif;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div style="font-size:20px; font-weight:600; letter-spacing:0.13em; text-transform:uppercase; color:rgba(255,255,255,0.85);">{s1['tag']}</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:22px; font-weight:700; color:rgba(255,255,255,0.6);">01 / 05</div>
      </div>
      <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
        <div style="font-size:34px; font-weight:600; color:#fff; margin-bottom:28px; letter-spacing:0.04em;">{s1['eyebrow']}</div>
        <h1 style="font-family:'Plus Jakarta Sans',sans-serif; font-size:68px; font-weight:800; line-height:1.12; color:#fff; margin-bottom:36px;">{s1['title']}</h1>
        <p style="font-size:40px; line-height:1.55; color:#fff; font-weight:500; max-width:92%;">{s1['sub']}</p>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:flex-end;">
        <div style="font-size:22px; font-weight:500; color:rgba(255,255,255,0.7);">← Swipe →</div>
        {logo_white}
      </div>
    </div>

    <!-- SLIDE 2 -->
    <div id="slide-2" class="slide" style="background:#FFFFFF; border:2px solid #e8e8e8; width:1080px; height:1080px; padding:88px 96px; display:flex; flex-direction:column; justify-content:space-between; position:absolute; top:0; left:1100px; font-family:'Inter',sans-serif;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div style="font-size:20px; font-weight:600; letter-spacing:0.13em; text-transform:uppercase; color:#0F838F;">{s2['tag']}</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:22px; font-weight:700; color:rgba(15,131,143,0.35);">02 / 05</div>
      </div>
      <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:144px; font-weight:800; color:#EAC435; line-height:1; margin-bottom:16px;">{s2.get('step','01')}</div>
        <h2 style="font-family:'Plus Jakarta Sans',sans-serif; font-size:62px; font-weight:800; line-height:1.15; color:#1B1B1B; margin-bottom:32px;">{s2['title']}</h2>
        <p style="font-size:32px; line-height:1.6; color:#333; max-width:90%;">{s2['body']}</p>
      </div>
      <div style="height:6px; background:#f0f0f0; border-radius:4px; overflow:hidden;">
        <div style="width:25%; height:100%; background:#0F838F; border-radius:4px;"></div>
      </div>
    </div>

    <!-- SLIDE 3 -->
    <div id="slide-3" class="slide" style="background:#FFFFFF; border:2px solid #e8e8e8; width:1080px; height:1080px; padding:88px 96px; display:flex; flex-direction:column; justify-content:space-between; position:absolute; top:0; left:2200px; font-family:'Inter',sans-serif;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div style="font-size:20px; font-weight:600; letter-spacing:0.13em; text-transform:uppercase; color:#0F838F;">{s3['tag']}</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:22px; font-weight:700; color:rgba(15,131,143,0.35);">03 / 05</div>
      </div>
      <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:144px; font-weight:800; color:#EAC435; line-height:1; margin-bottom:16px;">{s3.get('step','02')}</div>
        <h2 style="font-family:'Plus Jakarta Sans',sans-serif; font-size:62px; font-weight:800; line-height:1.15; color:#1B1B1B; margin-bottom:32px;">{s3['title']}</h2>
        <p style="font-size:32px; line-height:1.6; color:#333; max-width:90%;">{s3['body']}</p>
      </div>
      <div style="height:6px; background:#f0f0f0; border-radius:4px; overflow:hidden;">
        <div style="width:50%; height:100%; background:#0F838F; border-radius:4px;"></div>
      </div>
    </div>

    <!-- SLIDE 4 -->
    <div id="slide-4" class="slide" style="background:#FFFFFF; border:2px solid #e8e8e8; width:1080px; height:1080px; padding:88px 96px; display:flex; flex-direction:column; justify-content:space-between; position:absolute; top:0; left:3300px; font-family:'Inter',sans-serif;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div style="font-size:20px; font-weight:600; letter-spacing:0.13em; text-transform:uppercase; color:#0F838F;">{s4['tag']}</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:22px; font-weight:700; color:rgba(15,131,143,0.35);">04 / 05</div>
      </div>
      <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:144px; font-weight:800; color:#EAC435; line-height:1; margin-bottom:16px;">{s4.get('step','03')}</div>
        <h2 style="font-family:'Plus Jakarta Sans',sans-serif; font-size:62px; font-weight:800; line-height:1.15; color:#1B1B1B; margin-bottom:32px;">{s4['title']}</h2>
        <p style="font-size:32px; line-height:1.6; color:#333; max-width:90%;">{s4['body']}</p>
      </div>
      <div style="height:6px; background:#f0f0f0; border-radius:4px; overflow:hidden;">
        <div style="width:75%; height:100%; background:#0F838F; border-radius:4px;"></div>
      </div>
    </div>

    <!-- SLIDE 5 : CTA -->
    <div id="slide-5" class="slide" style="background:#EAC435; width:1080px; height:1080px; padding:88px 96px; display:flex; flex-direction:column; justify-content:space-between; position:absolute; top:0; left:4400px; font-family:'Inter',sans-serif;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div style="font-size:20px; font-weight:600; letter-spacing:0.13em; text-transform:uppercase; color:rgba(0,0,0,0.4);">{s5['tag']}</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:22px; font-weight:700; color:rgba(0,0,0,0.25);">05 / 05</div>
      </div>
      <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
        <div style="font-size:28px; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; color:rgba(0,0,0,0.65); margin-bottom:32px;">{s5['cta_label']}</div>
        <h2 style="font-family:'Plus Jakarta Sans',sans-serif; font-size:64px; font-weight:800; line-height:1.15; color:#1B1B1B; margin-bottom:40px;">{s5['title']}</h2>
        <div style="display:inline-flex; align-items:center; gap:16px; background:#0F838F; color:#fff; font-size:26px; font-weight:600; padding:24px 44px; border-radius:16px; width:fit-content;">{s5['btn']} →</div>
        <p style="font-size:28px; font-weight:600; color:rgba(0,0,0,0.6); margin-top:28px;">{s5['sub']}</p>
      </div>
      <div style="display:flex; justify-content:flex-end; align-items:flex-end;">
        <svg width="180" height="55" viewBox="0 0 360 110" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs><linearGradient id="rD2" x1="38" y1="14" x2="94" y2="96" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#63C6A6"/><stop offset="55%" stop-color="#3B8BC6"/><stop offset="100%" stop-color="#2F5BDB"/></linearGradient></defs>
          <circle cx="70" cy="55" r="34" stroke="url(#rD2)" stroke-width="10" stroke-linecap="round" fill="none" stroke-dasharray="180 60" stroke-dashoffset="18"/>
          <path d="M54 55.5L66 67.5L88 43" stroke="#3B8BC6" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          <text x="120" y="70" font-family="Inter,sans-serif" font-size="52" font-weight="700" fill="#1B1B1B" letter-spacing="-0.5">Exercia</text>
        </svg>
      </div>
    </div>
    """

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ width: 1080px; height: 1080px; overflow: hidden; position: relative; }}
.hook-accent {{ color: #EAC435; }}
.ct-accent {{ color: #0F838F; }}
</style>
</head>
<body>
{slides_html}
</body>
</html>"""



# ══════════════════ FORMAT "STORY 7" — Tu perds ton temps si… ══════════════════
# 7 slides 1080×1350 (4:5) : hook teal → problème teal → conséquence noir →
# data teal (barres) → solution teal → pratique noir (bullets) → CTA noir.

TEAL = "#0F838F"
DARK = "#14181B"
YELLOW = "#EAC435"
RED = "#E5484D"

DEFAULT_STORY7 = {
    "format": "story7",
    "slide1": {"sub": "Tu fais encore des <span class='u'>fiches</span> de révision pour le CRPE"},
    "slide2": {"body": "Recopier un cours, c'est confortable. Ton cerveau a l'impression de travailler.\n\nMais relire de l'information ne crée pas de <span class='u'>mémoire durable</span>."},
    "slide3": {"body": "Tu passes 2h à faire une belle fiche.\nTu la relis 3 jours plus tard.\n<span class='red'>Le jour J</span>, <b>tu ne t'en <span class='u'>souviens plus</span>.</b>"},
    "slide4": {"chart_title": "Rétention d'information après 1 semaine :",
               "bar1_label": "Récupération Active", "bar1_value": 70,
               "bar2_label": "Relecture Simple", "bar2_value": 20,
               "footer": "Ton cerveau retient ce qu'il doit retrouver, pas ce qu'on lui montre."},
    "slide5": {"body": "Tu fais des <span class='u'>exercices</span>.\nDès le départ.\nSans avoir “tout révisé”.\nL'erreur est une information précieuse."},
    "slide6": {"bullets": ["20 min d'exercices > 2h de fiches.",
                            "Cible tes lacunes réelles (pas tes préférences).",
                            "Répète ce qui coince jusqu'à automatisation.",
                            "Avance un peu chaque jour."]},
    "slide7": {"sub": "Pour y revenir avant ta prochaine session de révision"}
}

def _logo_lockup(size=1.0):
    """Logo Exercia blanc (icône + texte), échelle paramétrable."""
    w = int(300 * size)
    return f"""<svg width="{w}" viewBox="0 0 360 110" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="70" cy="55" r="34" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round" fill="none" stroke-dasharray="180 60" stroke-dashoffset="18"/>
      <path d="M54 55.5L66 67.5L88 43" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <text x="120" y="70" font-family="Inter,sans-serif" font-size="52" font-weight="700" fill="#FFFFFF" letter-spacing="-0.5">Exercia</text>
    </svg>"""

def _s7_header(show_logo=True):
    logo = _logo_lockup(0.95) if show_logo else ""
    return f"""
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <div>{logo}</div>
      <div style="border:3px solid rgba(255,255,255,0.9); border-radius:40px; padding:12px 30px;
                  font-family:'Inter',sans-serif; font-size:26px; font-weight:600; color:#fff;
                  letter-spacing:0.06em;">STRATÉGIE CRPE</div>
    </div>"""

def _s7_footer():
    return """
    <div style="display:flex; justify-content:center; align-items:center; gap:14px;">
      <svg width="26" height="32" viewBox="0 0 24 30"><path d="M2 2h20v26l-10-8-10 8z" fill="#fff"/></svg>
      <span style="font-family:'Inter',sans-serif; font-size:27px; color:rgba(255,255,255,0.92);">Enregistre — ça te servira</span>
    </div>"""

def _s7_slide(bg, body_html, show_logo=True, show_footer=True):
    footer = _s7_footer() if show_footer else "<div></div>"
    return f"""
    <div class="slide" style="background:{bg}; width:1080px; height:1350px; padding:70px 76px;
         display:flex; flex-direction:column; justify-content:space-between;
         font-family:'Inter',sans-serif; position:absolute; top:0;">
      {_s7_header(show_logo)}
      <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">{body_html}</div>
      {footer}
    </div>"""

def _s7_title(text, size=96):
    return f"""<h1 style="font-family:'Plus Jakarta Sans',sans-serif; font-size:{size}px; font-weight:800;
        text-transform:uppercase; line-height:1.05; color:#fff; letter-spacing:0.01em;
        margin-bottom:56px;">{text}</h1>"""

def build_html_story7(content):
    c = {**DEFAULT_STORY7}
    for k, v in content.items():
        if isinstance(v, dict) and k in c and isinstance(c.get(k), dict):
            c[k] = {**c[k], **v}
        else:
            c[k] = v

    css_common = """
      .u { text-decoration: underline; text-decoration-color: """ + YELLOW + """; text-decoration-thickness: 9px; text-underline-offset: 16px; text-decoration-skip-ink: none; }
      .red { color: """ + RED + """; font-weight: 700; }
      b { font-weight: 700; color: #fff; }
    """

    body_style = ("font-family:'Inter',sans-serif; font-size:44px; font-weight:500; line-height:1.75; "
                  "text-transform:uppercase; color:rgba(255,255,255,0.96); letter-spacing:0.01em; white-space:pre-line;")
    body_style_dark = body_style.replace("rgba(255,255,255,0.96)", "rgba(255,255,255,0.62)")

    # S1 — hook
    s1 = _s7_slide(TEAL,
        _s7_title("Tu perds ton<br>temps si…", 104) +
        f"<p style=\"{body_style}\">{c['slide1']['sub']}</p>")

    # S2 — le problème
    s2 = _s7_slide(TEAL,
        _s7_title("Le problème") +
        f"<p style=\"{body_style}\">{c['slide2']['body']}</p>")

    # S3 — ce que ça donne vraiment (noir)
    s3 = _s7_slide(DARK,
        _s7_title("Ce que ça donne<br>vraiment", 88) +
        f"<p style=\"{body_style_dark}\">{c['slide3']['body']}</p>")

    # S4 — data barres
    s4d = c['slide4']
    def bar(label, value):
        v = max(5, min(100, int(value)))
        return f"""
        <div style="display:flex; align-items:center; gap:36px; margin-bottom:44px;">
          <div style="width:280px; font-family:'Inter',sans-serif; font-size:36px; font-weight:700; color:#fff; line-height:1.25;">{label}</div>
          <div style="flex:1; height:86px; background:#3F4850; border-radius:22px; overflow:hidden; position:relative;">
            <div style="width:{v}%; height:100%; background:{YELLOW}; border-radius:22px; display:flex; align-items:center; padding-left:34px;">
              <span style="font-family:'Inter',sans-serif; font-size:38px; font-weight:800; color:#2A2E33;">{v}%</span>
            </div>
          </div>
        </div>"""
    s4 = _s7_slide(TEAL,
        _s7_title("Pourquoi ça ne<br>fonctionne pas", 88) +
        f"<div style=\"font-family:'Inter',sans-serif; font-size:40px; font-weight:700; color:#fff; margin-bottom:52px;\">{s4d['chart_title']}</div>" +
        bar(s4d['bar1_label'], s4d['bar1_value']) +
        bar(s4d['bar2_label'], s4d['bar2_value']) +
        f"<p style=\"{body_style} margin-top:36px;\">{s4d['footer']}</p>")

    # S5 — solution
    s5 = _s7_slide(TEAL,
        _s7_title("Ce que tu fais<br>à la place", 92) +
        f"<p style=\"{body_style}\">{c['slide5']['body']}</p>")

    # S6 — en pratique (noir, bullets)
    bullets = "".join(
        f"""<div style="display:flex; gap:26px; margin-bottom:42px; align-items:flex-start;">
              <div style="min-width:16px; height:16px; border-radius:50%; background:{TEAL}; margin-top:22px;"></div>
              <div style="font-family:'Inter',sans-serif; font-size:42px; color:rgba(255,255,255,0.95); line-height:1.5;">{b}</div>
            </div>"""
        for b in c['slide6']['bullets'][:4])
    s6 = _s7_slide(DARK,
        f"<div style=\"text-align:center;\">{_s7_title('En pratique', 96)}</div>" + bullets,
        show_logo=True)

    # S7 — CTA final (noir, lockup bas)
    s7_body = f"""
      <h1 style="font-family:'Plus Jakarta Sans',sans-serif; font-size:88px; font-weight:800;
          text-transform:uppercase; color:{YELLOW}; line-height:1.08; margin-bottom:48px;">Sauvegarde ce post</h1>
      <p style="font-family:'Inter',sans-serif; font-size:46px; font-weight:600; color:rgba(255,255,255,0.6);
          line-height:1.5; margin-bottom:110px;">{c['slide7']['sub']}</p>
      <div style="display:flex; align-items:center; gap:30px;">
        {_logo_lockup(0.85)}
        <div style="width:6px; height:56px; background:{TEAL};"></div>
        <span style="font-family:'Inter',sans-serif; font-size:40px; font-weight:700; color:{YELLOW};">entraîne-toi intelligemment</span>
      </div>"""
    s7 = _s7_slide(DARK, s7_body, show_logo=False, show_footer=False)

    slides = [s1, s2, s3, s4, s5, s6, s7]
    positioned = []
    for i, s in enumerate(slides):
        positioned.append(s.replace('position:absolute; top:0;', f'position:absolute; top:0; left:{i*1100}px;'))

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>* {{ box-sizing:border-box; margin:0; padding:0; }} body {{ width:1080px; height:1350px; overflow:hidden; position:relative; }} {css_common}</style>
</head><body>{''.join(positioned)}</body></html>"""

def export_slides_story7(content, out_dir):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    html = build_html_story7(content)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        page.set_content(html)
        page.wait_for_timeout(1200)
        for i in range(7):
            page.evaluate(f"document.body.style.transform = 'translateX(-{i*1100}px)'")
            page.wait_for_timeout(100)
            page.screenshot(path=os.path.join(out_dir, f"slide_{i+1:02d}.png"),
                            clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
            print(f"✓ slide_{i+1:02d}.png")
        browser.close()
    print(f"\nDone → {out_dir}")

# ── Export ─────────────────────────────────────────────────────────────────────

def export_slides(content: dict, out_dir: str):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    html = build_html(content)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        page.set_content(html)
        page.wait_for_timeout(1200)  # laisser les polices Google charger

        offsets = [0, 1100, 2200, 3300, 4400]

        for i, offset in enumerate(offsets):
            slide_num = i + 1
            out_path = os.path.join(out_dir, f"slide_{slide_num:02d}.png")

            page.evaluate(f"document.body.style.transform = 'translateX(-{offset}px)'")
            page.wait_for_timeout(100)

            page.screenshot(
                path=out_path,
                clip={"x": 0, "y": 0, "width": 1080, "height": 1080}
            )
            print(f"✓ slide_{slide_num:02d}.png")

        browser.close()

    print(f"\nDone → {out_dir}")

# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export carousel Exercia en PNG")
    parser.add_argument("--content", help="Chemin vers un fichier JSON de contenu", default=None)
    parser.add_argument("--out", help="Dossier de sortie", default="./carousel_output")
    args = parser.parse_args()

    if args.content:
        with open(args.content, "r", encoding="utf-8") as f:
            content = json.load(f)
    else:
        content = DEFAULT_CONTENT

    if content.get("format") == "story7":
        export_slides_story7(content, args.out)
    else:
        export_slides(content, args.out)
