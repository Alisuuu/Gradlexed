#!/usr/bin/env python3
"""Extract paths from test/drawable XML files and generate shapes.json"""
import os, re, json

DRAWABLE_DIR = "/sdcard/Download/dev/xmlpro/projeto/test/drawable"
OUTPUT_JSON = "/sdcard/Download/dev/xmlpro/projeto/app/src/main/assets/shapes.json"
OUTPUT_KT = "/sdcard/Download/dev/xmlpro/projeto/app/src/main/java/com/nomedoprojeto/generators/ShapeLibrary.kt"

CATEGORIES = {
    "bg1": "Backgrounds", "bg2": "Backgrounds", "bg3": "Backgrounds",
    "bg4": "Backgrounds", "bg5": "Backgrounds", "bg6": "Backgrounds",
    "bg7": "Backgrounds", "bg8": "Backgrounds", "bg9": "Backgrounds",
    "bg10": "Backgrounds",
    "bg_btn_pill": "Btn Pills", "bg_btn_style": "Btn Styles",
    "bg_game_panel": "Game Panels", "bg_gamer": "Gamer",
    "bg_notif": "Notifications", "bg_pill": "Pills", "bg_side": "Side Panels",
    "bg_squircle": "Icons", "bg_widget": "Widgets",
    "broom": "Icons", "bt": "Icons",
    "overlay_lightning": "Overlays",
}

def get_category(base_name):
    for prefix, cat in CATEGORIES.items():
        if base_name.startswith(prefix):
            return cat
    return "Outros"

def parse_color(color_str):
    if not color_str:
        return None
    color_str = color_str.strip()
    if color_str.startswith("@android:"):
        return None
    if color_str.startswith("#"):
        c = color_str[1:]
        if len(c) in (6, 8):
            return f"#{c}"
    return None

def fix_path(path_data):
    if not path_data:
        return ""
    path_data = re.sub(r'\s+', ' ', path_data.strip())
    path_data = re.sub(r'\s*,\s*', ',', path_data)
    path_data = re.sub(r',+', ',', path_data)
    path_data = path_data.strip(',')
    return path_data

def parse_xml_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    vp_w_match = re.search(r'android:viewportWidth="([^"]+)"', content)
    vp_h_match = re.search(r'android:viewportHeight="([^"]+)"', content)
    if not vp_w_match or not vp_h_match:
        return None
    try:
        vp_w = float(vp_w_match.group(1))
        vp_h = float(vp_h_match.group(1))
    except:
        return None

    path_pattern = re.compile(r'<path\s([^>]*?)/>', re.DOTALL)
    paths = []

    for pm in path_pattern.finditer(content):
        attrs = pm.group(1)
        pd_match = re.search(r'android:pathData="([^"]*)"', attrs, re.DOTALL)
        if not pd_match:
            continue
        raw_path = pd_match.group(1).strip()
        if not raw_path:
            continue
        path_data = fix_path(raw_path)
        if not path_data:
            continue

        fill_match = re.search(r'android:fillColor="([^"]*)"', attrs)
        stroke_match = re.search(r'android:strokeColor="([^"]*)"', attrs)
        sw_match = re.search(r'android:strokeWidth="([^"]*)"', attrs)
        alpha_match = re.search(r'android:fillAlpha="([^"]*)"', attrs)

        fill_color = parse_color(fill_match.group(1)) if fill_match else None
        stroke_color = parse_color(stroke_match.group(1)) if stroke_match else None
        stroke_width = float(sw_match.group(1)) if sw_match else 0.0
        fill_alpha = float(alpha_match.group(1)) if alpha_match else 1.0

        if not fill_color and not stroke_color:
            stroke_color = "#FFFFFF"

        paths.append({
            'pathData': path_data,
            'fillColor': fill_color,
            'strokeColor': stroke_color,
            'strokeWidth': stroke_width,
            'fillAlpha': fill_alpha,
        })

    if not paths:
        return None

    return {
        'vpW': vp_w,
        'vpH': vp_h,
        'paths': paths,
    }

def main():
    all_shapes = []
    for filename in sorted(os.listdir(DRAWABLE_DIR)):
        if not filename.endswith('.xml'):
            continue
        filepath = os.path.join(DRAWABLE_DIR, filename)
        info = parse_xml_file(filepath)
        if not info:
            continue
        base_name = filename.replace('.xml', '')
        cat = get_category(base_name)
        for pi, p in enumerate(info['paths']):
            all_shapes.append({
                'id': f"{base_name}_p{pi}",
                'name': f"{base_name.replace('_', ' ').title()} P{pi}",
                'pathData': p['pathData'],
                'fillColor': p['fillColor'],
                'strokeColor': p['strokeColor'],
                'strokeWidth': p['strokeWidth'],
                'fillAlpha': p['fillAlpha'],
                'category': cat,
                'vpW': info['vpW'],
                'vpH': info['vpH'],
            })

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_shapes, f)

    # Generate lightweight ShapeLibrary.kt that loads from JSON
    kt_code = '''package com.nomedoprojeto.generators

import android.content.Context
import androidx.compose.ui.graphics.Color

data class ShapeDef(
    val id: String,
    val name: String,
    val pathData: String,
    val fillColor: Color,
    val strokeColor: Color? = null,
    val strokeWidth: Float = 0f,
    val category: String,
    val sourceViewportW: Float = 100f,
    val sourceViewportH: Float = 100f
)

object ShapeLibrary {

    private var _all: List<ShapeDef>? = null

    private fun hex(color: String): Color = Color(android.graphics.Color.parseColor(color))

    fun init(context: Context) {
        if (_all != null) return
        val json = context.assets.open("shapes.json").bufferedReader().use { it.readText() }
        val arr = org.json.JSONArray(json)
        val list = mutableListOf<ShapeDef>()
        for (i in 0 until arr.length()) {
            val obj = arr.getJSONObject(i)
            val fc = obj.optString("fillColor", null)
            val sc = obj.optString("strokeColor", null)
            list.add(ShapeDef(
                id = obj.getString("id"),
                name = obj.getString("name"),
                pathData = obj.getString("pathData"),
                fillColor = if (fc != null) hex(fc) else Color.Transparent,
                strokeColor = if (sc != null) hex(sc) else null,
                strokeWidth = obj.optDouble("strokeWidth", 0.0).toFloat(),
                category = obj.getString("category"),
                sourceViewportW = obj.optDouble("vpW", 100.0).toFloat(),
                sourceViewportH = obj.optDouble("vpH", 100.0).toFloat()
            ))
        }
        _all = list
    }

    val all: List<ShapeDef>
        get() = _all ?: emptyList()

    fun getById(id: String): ShapeDef? = all.find { it.id == id }
    fun categories(): List<String> = all.map { it.category }.distinct().sorted()
}
'''
    with open(OUTPUT_KT, 'w', encoding='utf-8') as f:
        f.write(kt_code)

    print(f"Generated {len(all_shapes)} shapes -> shapes.json + ShapeLibrary.kt")

if __name__ == '__main__':
    main()
