import csv, requests, json
import logging
import yaml

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

deont_modalities = {
    None: 0,
    "permission": 1,
    "prohibition": 2,
    "obligation": 3
}

def write(data):
    options = [o for o in data if o['type'] == 'Option']
    deeds = [d for d in data if d['type'] == 'Deed']

    rows = []
    for opt in options:
        try:
            text, t_type, general_rule, deontic_modality = get_values(opt)
            rows.append({
                "text": text,
                "t_type": t_type,
                "general_rule": general_rule,
                "deontic_modality": deontic_modality
            })
        except KeyError: pass

    for d in deeds:
        try:
            text, t_type, general_rule, deontic_modality = get_values(d)
            rows.append({
                "text": text,
                "t_type": t_type,
                "general_rule": general_rule,
                "deontic_modality": deontic_modality
            })
        except KeyError: pass

    try:
        endpoint = yaml.load(open('endpoints.yml'), Loader=yaml.FullLoader)['append']
    except AttributeError:
        logger.warning('Could not determine endpoint for append')

    try:
        r = requests.post(endpoint, json=rows, timeout=20)
        
        if not r.status_code == 200:
            logger.warning('Could not write moral data to model server.')
    except requests.exceptions.ConnectionError:
        logger.warning('Could not connect to model server')

def get_values(ent):
    try:
        text = ent['label']
        t_type = 'opt' if ent['type'] == 'Option' else 'act'
        general_rule = 1 if ent['universalizable'] == True else 0
        deontic_modality = deont_modalities[ent['deontic_modality']]
    except KeyError: raise

    return (text, t_type, general_rule, deontic_modality)