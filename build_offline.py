"""Build self-contained browser app without third-party assets or network requests."""
from pathlib import Path
p=Path(__file__).resolve().parent
html=(p/'index.html').read_text(encoding='utf-8')
html=html.replace('<link rel="stylesheet" href="styles.css">','<style>\n'+(p/'styles.css').read_text(encoding='utf-8')+'\n</style>')
for name in ['engine.js','app.js']:
    html=html.replace('<script src="'+name+'"></script>','<script>\n'+(p/name).read_text(encoding='utf-8')+'\n</script>')
(p/'JPO_DSS_OFFLINE.html').write_text(html,encoding='utf-8')
print('Built', (p/'JPO_DSS_OFFLINE.html').stat().st_size, 'bytes')