import json
import pandas as pd
import random
import uploader
import os
import logging

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class UtilitarismEvaluation():
    def __init__(self, json_data):
        self.data = json_data
        self.url = ''
        self.success = False
        self.result = self.build_decision_table()

        try:
            self.result_txt = self.result.to_string()
        except AttributeError:
            self.result_txt = ''

        self.image = self.plot_image()

    def get_result(self):
        result = {
            'url': self.url,
            'text': self.result_txt,
            'success': self.success
        }
        return result

    def upload(self):
        self.url = uploader.upload(self.image, 'utilitarism')
        os.remove(self.image)
        return self.url

    def plot_image_html(self):

        data = self.result
        with open ("utilitarism/style.css", "r") as ss:
            css = ss.read()

        fn = str(random.random()*100000000).split(".")[0] + ".html"       
        text_file = open(fn, "a")

        text_file.write(css)
        text_file.write(data.to_html())
        text_file.close()

        fn_out = 'util_' + str(random.getrandbits(128)) + '.png'

        # TODO
        # Find suiting method to convert html file to image

        os.remove(fn)
        return fn_out

    def plot_image(self):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(3, 2))
        ax.axis('off')

        # caption describing the formula
        #formula = 'Score = ∑ Amount of persons × Moral status weight × Impact(c) × Probability(c)'
        formula = r'$Score = \sum_{i=0}^{consequences} N\:×\:W\:×\:I(c_i)\:×\:P(c_i)$'

        description = 'The utilitarian score per person/group is computed by the formula:\n {} \n \
            N = Number of persons \
            W = Moral status weight \n \
            I = Consequence impact \
            P = Consequence probability'.format(formula)
        plt.figtext(0.4, -0.4, description, wrap=True, horizontalalignment='center', fontsize=10)
        
        ax.table(
                cellText=self.result.values, 
                colLabels=self.result.columns,
                rowLabels=self.result.index,
                colWidths=[1 for c in self.result.columns],
                loc='center'
        )
        
        filename = 'util_' + str(random.getrandbits(128)) + '.png'
        plt.savefig(filename, bbox_inches='tight')

        plt.close()

        return filename


    def build_decision_table(self):
        options = [o for o in self.data if o['type'] == 'Option']
        stakeholders = [s for s in self.data if s['type'] == 'Stakeholder']
        consequences = [c for c in self.data if c['type'] == 'Consequence']

        try:
            opt_columns = [opt['label'] for opt in options]
        except AttributeError as e:
            logger.warning('Missing label in option: {}'.format(e))
        
        df = pd.DataFrame(columns=opt_columns)
            
        for sh in stakeholders:
            row = []
            try:
                for opt in options:
                    imp = 0
                    for cons in consequences:
                        if (sh['name'] in cons['affected_stakeholders']) and (cons['option'] == opt['id']):
                            # If amount is unknown, assume factor 2 (not much more that can be done here...)
                            if sh['amount'] == -1: sh['amount'] = 2
                            imp += cons['impact'] * cons['probability'] * sh['amount'] * sh['moral_status_weight']
                    row.append(round(imp, 2))
                df.loc[sh['name']] = row
            except (AttributeError, KeyError) as e:
                logger.warning('Exception computing utilitarian score: {}'.format(e))
        df.loc['Total'] = round(df.sum(), 2)
        
        self.success = True
        return df

    def __repr__(self):
        return self.result_txt
    
    def __str__(self):
        return self.__repr__()