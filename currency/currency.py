import json

from lxml import etree

from urllib import request
from urllib.parse import urlencode, quote_plus

CONVERSION_URL_PATTERN = 'https://www.google.com/finance/converter?{query}'
CONVERSION_RESULT_XPATH = '//*[@id="currency_converter_result"]/span'


def convert_currency(amount, source_currency_code, target_currency_code):
    args = {'a': amount,
            'from': source_currency_code,
            'to': target_currency_code}
    query = urlencode(args, quote_via=quote_plus)
    url = CONVERSION_URL_PATTERN.format(query=query)

    with request.urlopen(url) as response:
        response_html = response.read()

    root = etree.HTML(response_html)
    result_element = root.xpath(CONVERSION_RESULT_XPATH).pop()

    result = float(result_element.text.split().pop(0))

    return result


class Campaign(object):
    def __init__(self, cid, name, cost, revenue, currency_code,
                 number_of_conversions):
        self.cid = cid
        self.name = name
        self.cost = cost
        self.revenue = revenue
        self.currency_code = currency_code
        self.number_of_conversions = number_of_conversions

    def calculate_total_profit(self):
        return self.number_of_conversions * (self.revenue - self.cost)

    def calculate_total_profit_in(self, currency_code):
        return convert_currency(self.calculate_total_profit(),
                                self.currency_code,
                                currency_code)

    def __repr__(self):
        return '<{class_name}({cid}, {name})>'.format(
            class_name=type(self).__name__,
            cid=self.cid,
            name=self.name
        )


def load_campaigns(filename):
    campaigns = []
    with open(filename) as handler:
        campaigns_data = json.load(handler)
    for data in campaigns_data:
        campaigns.append(Campaign(
            cid=data['id'],
            name=data['name'],
            cost=data['cost'],
            revenue=data['revenue'],
            currency_code=data['currency'],
            number_of_conversions=data['conversions']
        ))
    return campaigns


campaigns = load_campaigns('campaigns.json')

profits_data = []
for campaign in campaigns:
    profits_data.append({
        'id': campaign.cid,
        'name': campaign.name,
        'total_profit': campaign.calculate_total_profit_in('USD')
    })

print(json.dumps(profits_data, indent=4))
