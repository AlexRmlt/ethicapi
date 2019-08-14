from anytree import Node, RenderTree
from anytree.exporter import DotExporter
import uploader
import os, logging, random
import requests
import yaml

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DeontologyEvaluation():
    general_rule = {
        True: "General rule: Yes",
        False: "General rule: No"
    }

    deont_modalities = {
        "indifference": "",
        "permission": "Permission",
        "prohibition": "Prohibition",
        "obligation": "Obligation"
    }

    no_rule_reasons = {
        "no_reason": "",
        "inherently_evil": "this action can be considered inherently evil!",
        "too_specific": "a more general formulated rule could apply in this case!",
        "needs_conditions": "a general rule could be applied under certain conditions!"
    }

    def __init__(self, json_data):       
        self.data = json_data
        self.url = ''
        self.success = False
        self.result = self.build_tree()
        self.result_txt = self.tree_to_string(self.result)
        self.image = self.plot_image()

    def get_prediction(self, text):
        try:
            endpoint = yaml.load(open('endpoints.yml'), Loader=yaml.FullLoader)['predict']
        except AttributeError:
            logger.warning('Could not determine endpoint for predict')
            return None

        payload = { 't': text }
       
        try:
            r = requests.get(endpoint, params=payload, timeout=20)
        except requests.exceptions.ConnectionError:
            logger.warning('Could not connect to model server')
            return None, None

        try:
            gr = r.json()['general_rule']
            conf = r.json()['confidence']
        except AttributeError:
            logger.warning('Received no valid response from model server')
            return None, None

        return gr, conf

    def get_result(self):
        result = {
            'url': self.url,
            'text': self.result_txt,
            'success': self.success
        }
        return result

    def upload(self):
        self.url = uploader.upload(self.image, 'deontology')
        os.remove(self.image)
        return self.url

    def plot_image(self):
        filename = 'deont_' + str(random.getrandbits(128)) + '.png'
        DotExporter(self.result).to_picture(filename)

        return filename

    def get_node_info(self, ent):
        # 1. Could a general rule be wanted?
        univers = ''
        if ('universalizable' in ent):
            try:
                univers = '\n {}'.format(self.general_rule[ent['universalizable']])
            except KeyError as e:
                logger.warning('Could not determine general rule: {}'.format(e))

        # 2. If not, what ist the constraint?
        no_rule_reason = ''
        if ('no_rule_reason' in ent):
            if not ent['no_rule_reason'] == None:
                try:
                    no_rule_reason = '\n ({})'.format(self.no_rule_reasons[ent['no_rule_reason']])
                except KeyError as e:
                    logger.warning('Could not determine no rule reason: {}'.format(e))

        # 3. Which deontic modality can be assigned?
        deontic_modality = ''
        if ('deontic_modality' in ent):
            if not ent['deontic_modality'] == None:
                try:
                    deontic_modality = '\n Deontic modality: {}'.format(self.deont_modalities[ent['deontic_modality']])
                except KeyError as e:
                    logger.warning('Could not determine deontic modality: {}'.format(e))

        # 4. What is the verdict based on the data of other users?
        gr_prediction = ''
        if ('universalizable' in ent):
            gr, conf = self.get_prediction(ent['label'])
            if not (gr == None) and not (conf == None):
                gr_prediction = '\n\n Verdict for a general rule based on previous input: {} (confidence: {})'.format(gr, conf)

        return (univers, no_rule_reason, deontic_modality, gr_prediction)


    def build_tree(self):
        options = [o for o in self.data if o['type'] == 'Option']
        stakeholders = [s for s in self.data if s['type'] == 'Stakeholder']
        deeds = [d for d in self.data if d['type'] == 'Deed']

        # Identify decider (root node)
        decider = [s['name'] for s in stakeholders if s['decider'] == True][0]
        node_root = Node(decider)

        # Add options
        nodes_opt = dict()
        for opt in options:
            univers, no_rule_reason, deontic_modality, gr_prediction = self.get_node_info(opt)
            nodes_opt[opt['id']] = Node(opt['label'] + univers + no_rule_reason + deontic_modality + gr_prediction, parent=node_root)

        # Add deeds
        nodes_deed = dict()
        for d in deeds:
            univers, no_rule_reason, deontic_modality, gr_prediction = self.get_node_info(d)
            nodes_deed[d['id']] = Node(d['label'] + univers + no_rule_reason + deontic_modality + gr_prediction, parent=nodes_opt[d['option']])

        self.success = True
        return node_root
    
    def tree_to_string(self, t):
        tree = ''
        for pre, fill, node in RenderTree(t):
            tree = tree + str(pre) + str(node.name) + '\n'
        return tree 

    def __repr__(self):
        return self.result
    
    def __str__(self):
        return self.__repr__()