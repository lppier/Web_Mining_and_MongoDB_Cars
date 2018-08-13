from nltk import word_tokenize
import re


class Utility:
    def untokenize(self, words):
        text = ' '.join(words)
        step1 = text.replace("`` ", '"').replace(" ''", '"').replace('. . .', '...')
        step2 = step1.replace(" ( ", " (").replace(" ) ", ") ")
        step3 = re.sub(r' ([.,:;?!%]+)([ \'"`])', r"\1\2", step2)
        step4 = re.sub(r' ([.,:;?!%]+)$', r"\1", step3)
        step5 = step4.replace(" '", "'").replace(" n't", "n't").replace(
            "can not", "cannot")
        step6 = step5.replace(" ` ", " '")
        return step6.strip()

    # Returns [Manufacturer, Model, rest of string] tuple
    def manufacturer_and_model(self, str, manu_list, model_list):
        print(str)
        manu_model = []
        tokens = word_tokenize(str)
        tokens_lower = [token.lower() for token in tokens]
        for manufacturer in manu_list:
            if manufacturer.lower() in tokens_lower:
                manu_model.append(manufacturer)

        for model in model_list:
            if model.lower() in tokens_lower:
                manu_model.append(model)

        # del tokens[tokens.index(manu_model[0])]
        # del tokens[tokens.index(manu_model[1])]
        manu_model.append(self.untokenize(tokens))

        return manu_model

# test_str = "Honda Civic Type-R 2.0M VTEC Turbo GT"
# list_of_manufacturers =  ['Honda', 'Volkswagen', 'Ferrari', 'Nissan',
#                          'Toyota']  # to be replaced by mongo manufacturer query for "manufacturer"
# list_of_models_for_honda = ['Accord', 'Civic', 'Fit']  # to be replaced by mongo query for "honda models"
# test = manufacturer_and_model(test_str, list_of_manufacturers, list_of_models_for_honda)
# print(test)
