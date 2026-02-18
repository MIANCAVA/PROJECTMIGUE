import feedparser
import re
from newspaper import Article
from datetime import datetime
import urllib.parse

def get_google_news_rss(topic, region, lang, period):
    topic_encoded = urllib.parse.quote(topic)
    url = f"https://news.google.com/rss/search?q={topic_encoded}+when:{period}&hl={lang}-{region}&gl={region}&ceid={region}:{lang}"
    return url

def extract_people(text):
    if not text:
        return []
    pattern = r'(?<!\.\s)(?<!^)(?<!\")[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?'
    matches = re.findall(pattern, text)
    ignore_list = ['El Gobierno', 'La Fiscalía', 'La Policía', 'El Presidente', 'Los Jueces', 'Corte Supreme', 'Corte Constitucional', 'Banco Agrario', 'Naciones Unidas', 'Derechos Humanos', 'Santa Fe', 'San Andrés', 'Puerto Rico', 'Costa Rica', 'Nueva York', 'Reino Unido', 'Medicina Legal', 'Estados Unidos', 'Ministerio Público', 'Unión Europea', 'América Latina']
    
    clean_matches = []
    for m in matches:
        if m not in ignore_list and len(m) > 5:
            clean_matches.append(m)
            
    return sorted(list(set(clean_matches)))

def fetch_news(topics, region="CO", lang="es", period="7d", max_per_topic=20):
    all_results = []
    seen_links = set()
    
    for topic in topics:
        rss_url = get_google_news_rss(topic, region, lang, period)
        feed = feedparser.parse(rss_url)
        
        count = 0
        for entry in feed.entries:
            if count >= max_per_topic: break
            if entry.link in seen_links: continue
            
            seen_links.add(entry.link)
            count += 1
            
            article_data = {
                'Fecha Noticia': datetime.now().strftime("%Y-%m-%d"),
                'Link': entry.link,
                'Titulo': entry.title,
                'Resumen': '',
                'Personas Mencionadas': '',
                'Tema': topic
            }
            
            if hasattr(entry, 'published'):
                article_data['Fecha Noticia'] = entry.published
                
            try:
                art = Article(entry.link)
                art.download()
                art.parse()
                
                if art.text:
                    article_data['Resumen'] = art.text[:400]
                    people = extract_people(art.text)
                    article_data['Personas Mencionadas'] = ", ".join(people)
                else:
                    article_data['Resumen'] = entry.description if hasattr(entry, 'description') else "Contenido no disponible"
                
                if art.publish_date:
                    article_data['Fecha Noticia'] = str(art.publish_date)
                    
            except Exception:
                article_data['Resumen'] = entry.description if hasattr(entry, 'description') else ""
            
            article_data['Resumen'] = str(article_data['Resumen']).replace('\n', ' ').strip()
            all_results.append(article_data)
            
    return all_results
