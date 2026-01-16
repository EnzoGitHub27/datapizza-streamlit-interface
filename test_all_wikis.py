#!/usr/bin/env python3
"""
Test rapido di tutte le wiki pubbliche configurate
"""

from rag.adapters import MediaWikiAdapter

# Wiki pubbliche di test
TEST_WIKIS = [
    {
        "name": "Wikipedia IT",
        "url": "https://it.wikipedia.org",
        "categories": ["Intelligenza artificiale"],
        "max_pages": 3,
    },
    {
        "name": "Wikipedia EN",
        "url": "https://en.wikipedia.org",
        "categories": ["Artificial intelligence"],
        "max_pages": 3,
    },
    {
        "name": "Wikivoyage IT",
        "url": "https://it.wikivoyage.org",
        "categories": ["Italia"],
        "max_pages": 3,
    },
    {
        "name": "Wikibooks IT",
        "url": "https://it.wikibooks.org",
        "categories": ["Informatica"],
        "max_pages": 3,
    },
]

print("=" * 70)
print("🧪 TEST CONNESSIONE WIKI PUBBLICHE")
print("=" * 70)

results = []

for wiki_config in TEST_WIKIS:
    print(f"\n📡 Testing: {wiki_config['name']}")
    print(f"   URL: {wiki_config['url']}")
    print(f"   Categoria: {wiki_config['categories'][0]}")

    config = {
        "url": wiki_config["url"],
        "api_path": "/w/api.php",
        "namespaces": [0],
        "categories": wiki_config["categories"],
        "max_pages": wiki_config["max_pages"],
        "include_redirects": False,
        "timeout": 30,
    }

    try:
        adapter = MediaWikiAdapter(config)

        if adapter.connect():
            documents = adapter.load_documents()

            if documents:
                print(f"   ✅ OK - {len(documents)} pagine caricate")
                results.append((wiki_config['name'], True, len(documents)))

                # Mostra prima pagina
                doc = documents[0]
                title = doc.metadata.get("title", "N/A")
                print(f"   📄 Esempio: {title}")
            else:
                print(f"   ⚠️  Connessa ma nessuna pagina trovata")
                results.append((wiki_config['name'], False, 0))
        else:
            print(f"   ❌ Errore connessione")
            results.append((wiki_config['name'], False, 0))

    except Exception as e:
        print(f"   ❌ Errore: {e}")
        results.append((wiki_config['name'], False, 0))

# Riepilogo
print("\n" + "=" * 70)
print("📊 RIEPILOGO TEST")
print("=" * 70)

for name, success, count in results:
    status = "✅" if success else "❌"
    print(f"{status} {name:20} - {count} pagine")

success_count = sum(1 for _, s, _ in results if s)
print(f"\n🎯 Successo: {success_count}/{len(results)} wiki")
