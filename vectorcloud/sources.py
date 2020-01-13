import os
from jsmin import jsmin
from vectorcloud import app
from vectorcloud.paths import static_folder
from vectorcloud.cssmin import cssmin

"""This file establishes bundles of js and css sources, minifies them using jsmin and
a vectorcloud module named cssmin, adds script or style tag, uses a flask
context processor to make the process functions available to every jinja template.
Load orders in bundles are respected here"""

"""You can disable minification for debug purposes here (set to True) """
debug_js = True
debug_css = True


def process_js_sources(process_bundle=None, src=None, app_global=False):
    if src:
        process_bundle = [src]

    elif app_global is True:
        process_bundle = [
            "global/vectorcloud.js",
            "global/tcdrop.js",
        ]

    html = ""
    if debug_js is True:
        for source in process_bundle:
            html += f'<script src="static/js/{source}"></script>'
        return html
    for source in process_bundle:
        source_path = os.path.join(static_folder, "js", source)
        with open(source_path) as js_file:
            minified = jsmin(js_file.read(), quote_chars="'\"`")
            html += f"<script>{minified}</script>"

    return html


def process_css_sources(process_bundle=None, src=None, app_global=False):
    if src:
        process_bundle = [src]

    elif app_global is True:
        process_bundle = [
            "global/style.css",
            "global/vectorcloud-theme.css",
            "global/vectorcloud.css",
            "global/tcdrop.css",
        ]

    html = ""
    if debug_css is True:
        for source in process_bundle:
            html += (
                f'<link rel="stylesheet" type="text/css" '
                f'href="static/css/{source}">'
            )
        return html
    else:
        for source in process_bundle:
            source_path = os.path.join(static_folder, "css", source)
            minified = cssmin(source_path)
            html += f"<style>{minified}</style>"

    return html


@app.context_processor
def context_processor():
    return dict(
        test_key="test",
        process_js_sources=process_js_sources,
        process_css_sources=process_css_sources,
    )
