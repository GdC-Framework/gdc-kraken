# Fonctions utilitaires
from .models import Mission

def parse_mission_filename(filename):
    import re
    allowed_types = '|'.join([choice[0] for choice in Mission.TYPE_CHOICES])
    # Autorise lettres, chiffres, ponctuation, accents, caractères spéciaux clavier qwerty/azerty
    pattern = rf"^(CPC-({allowed_types})\[(\d{{2,3}})\]-[\w\d\s\-\_\(\)@#%&'éèàùâêîôûäëïöüçÉÈÀÙÂÊÎÔÛÄËÏÖÜÇ]+)-([Vv]\d+)\.(.+)\.pbo$"
    match = re.match(pattern, filename)
    if not match:
        return None
    return match.groups()


# LEGACY ONLY - Fonctions utilitaires pour l'import massif de missions .pbo
def legacy_parse_mission_filename(filename):
    # Expected output:
    # mission_name, mission_type, max_players, version, map_name
    import re
    allowed_types = '|'.join([choice[0] for choice in Mission.TYPE_CHOICES])
    # Autorise lettres, chiffres, ponctuation, accents, caractères spéciaux clavier qwerty/azerty
    #pattern = rf"^(CPC-({allowed_types})\[(\d{{2,3}})\]-?[\w\d\s\-\_\(\)@#%&'éèàùâêîôûäëïöüçÉÈÀÙÂÊÎÔÛÄËÏÖÜÇ]+)(?:[-_]([Vv]\d+))?\.(.+)\.pbo$"
    pattern = rf"^(CPC-({allowed_types})\[(\d{{2,3}})\]-?[\w\d\s\-\_\(\)@#%&'éèàùâêîôûäëïöüçÉÈÀÙÂÊÎÔÛÄËÏÖÜÇ]+)\.(.+)\.pbo$"
    match = re.match(pattern, filename)
    if not match:
        return None
    mission_name, mission_type, max_players, map_name = match.groups()
    
    pattern = rf"^(CPC-({allowed_types})\[(\d{{2,3}})\]-[\w\d\s\-\_\(\)@#%&'éèàùâêîôûäëïöüçÉÈÀÙÂÊÎÔÛÄËÏÖÜÇ]+)-([Vv]\d+)"
    match = re.match(pattern, filename)
    if not match:
        # Version non fournie, on met V1 par défaut
        version = "V1"
    else:
        groups = list(match.groups())
        mission_name = groups[0]
        version = groups[3]
    return mission_name, mission_type, max_players, version, map_name
