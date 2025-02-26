import re

def clean_code (dic):
    try:
        for key in dic.keys():
            #Reemplaza múltiples espacios por uno solo
            cleaned = re.sub(r'\s+', '', cleaned)
            
            #Elimina comentarios de python, javaScript y java
            cleaned = re.sub(r'#.*', '', cleaned) # Python: elimina comentarios #
            cleaned = re.sub(r'//.*', '', cleaned) # JS/Java: elimina comentarios //
            cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL) # JS/Java: bloque /* */
            
            dic[key] = cleaned.strip()
            
        return dic
    
    except Exception as e:
        print(f"⚠️ Failed to clean code: {e}")
        return None
