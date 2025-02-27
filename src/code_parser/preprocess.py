import re

def clean_code (dic):
    try:
        for key in dic.keys():
            cleaned = dic[key]
            
            # Validar urls
            urls = re.findall(r'https?://[^\s,"]+', cleaned)  # Encuentra URLs
            placeholders = {url: f"URL_PLACEHOLDER_{i}" for i, url in enumerate(urls)}

            for url, placeholder in placeholders.items():
                cleaned = cleaned.replace(url, placeholder)
            
            #Elimina comentarios de python, javaScript y java
            cleaned = re.sub(r'#.*', '', cleaned) # Python: elimina comentarios #
            cleaned = re.sub(r'//(?!URL_PLACEHOLDER_).*', '', cleaned) # JS/Java: elimina comentarios //
            cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL) # JS/Java: bloque /* */
            
            dic[key] = cleaned.strip()
            
        return dic
    
    except Exception as e:
        print(f"⚠️  Failed to clean code: {e}")
        return None
