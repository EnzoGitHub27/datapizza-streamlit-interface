#!/usr/bin/env python3
"""
Test rapido connessione Wikipedia
"""

from rag.adapters import MediaWikiAdapter

# Configurazione Wikipedia IT
config = {
    "url": "https://it.wikipedia.org",
    "api_path": "/w/api.php",
    "namespaces": [0],
    "categories": ["Intelligenza artificiale"],
    "max_pages": 5,  # Solo 5 pagine per test veloce
    "include_redirects": False,
    "timeout": 30,
}

print("🔍 Test connessione Wikipedia IT...")
print(f"📋 Categoria: {config['categories'][0]}")
print(f"📄 Limite: {config['max_pages']} pagine\n")

# Crea adapter
adapter = MediaWikiAdapter(config)

# Test connessione
print("🌐 Connessione in corso...")
if adapter.connect():
    print("✅ Connessione riuscita!\n")

    # Carica documenti
    print("📥 Caricamento pagine...")

    def progress_callback(progress, status):
        print(f"   {status} ({progress*100:.0f}%)")

    documents = adapter.load_documents(progress_callback=progress_callback)

    print(f"\n✅ Caricamento completato!")
    print(f"📊 Pagine caricate: {len(documents)}\n")

    # Mostra le prime 3 pagine
    print("📄 Prime pagine caricate:")
    for i, doc in enumerate(documents[:3], 1):
        title = doc.metadata.get("title", "N/A")
        url = doc.metadata.get("page_url", "N/A")
        content_preview = doc.content[:150].replace("\n", " ")
        print(f"\n{i}. {title}")
        print(f"   🔗 {url}")
        print(f"   📝 {content_preview}...")

else:
    print("❌ Errore connessione")
