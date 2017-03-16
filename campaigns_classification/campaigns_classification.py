# -*- coding: utf-8 -*-
import json
import sys


ALL = None


def evaluate_string(user_value, campaing_value):
    return (0.75 if campaing_value == ALL else
            1.0 if user_value.lower() == campaing_value.lower() else
            0.0)


class Campaign(object):
    def __init__(self, cid, name, gender=ALL, min_age=0, max_age=sys.maxsize,
                 platform=ALL, connection=ALL):
        self.cid = cid
        self.name = name
        self.gender = gender
        self.min_age = min_age
        self.max_age = max_age
        self.platform = platform
        self.connection = connection

    def evaluate_age(self, age):
        age_avg = (self.max_age + self.min_age) / 2
        age_dev = age_avg - self.min_age
        return max(0, 1 - abs(age - age_avg)/age_dev)

    def evaluate_user(self, user):
        return (0.2 * self.evaluate_age(user.age) +
                0.3 * evaluate_string(user.gender, self.gender) +
                0.25 * evaluate_string(user.platform, self.platform) +
                0.25 * evaluate_string(user.connection, self.connection))

    def __repr__(self):
        return '<{class_name}({cid}, {name})>'.format(
            class_name=type(self).__name__,
            cid=self.cid,
            name=self.name
        )


class User(object):
    def __init__(self, username, gender, age, platform, connection):
        self.username = username
        self.gender = gender
        self.age = age
        self.platform = platform
        self.connection = connection

    def fits_campaign(self, campaign):
        return (campaign.min_age <= self.age <= campaign.max_age and
                evaluate_string(self.gender, campaign.gender) and
                evaluate_string(self.platform, campaign.platform) and
                evaluate_string(self.connection, campaign.connection))


class Classifier(object):
    _fitting_campaigns = None

    def __init__(self, user, campaigns):
        self._user = user
        self._campaigns = campaigns

    @property
    def user(self):
        return self._user

    @property
    def campaigns(self):
        return self._campaigns

    @property
    def fitting_campaigns(self):
        if self._fitting_campaigns is None:
            self._fitting_campaigns = [campaign for campaign in self.campaigns
                                       if self.user.fits_campaign(campaign)]
        return self._fitting_campaigns

    def get_best_campaign(self):
        return max(
            self.fitting_campaigns,
            key=lambda campaign: campaign.evaluate_user(self.user)
        )


def load_campaigns(filename):
    campaigns = []
    with open(filename) as handler:
        campaigns_data = json.load(handler)
    for data in campaigns_data:
        kwargs = {
            'cid': data['id'],
            'name': data['name'],
        }

        if data['min_age']:
            kwargs['min_age'] = data['min_age']
        if data['max_age']:
            kwargs['max_age'] = data['max_age']

        for key in ['gender', 'platform', 'connection']:
            if data[key].lower() != 'all':
                kwargs[key] = data[key]

        campaigns.append(Campaign(**kwargs))
    return campaigns

def load_user(filename):
    with open(filename) as handler:
        data = json.load(handler)
    return User(data['username'], data['gender'], data['age'],
                data['platform'], data['connection'])


user = load_user('user.json')
campaigns = load_campaigns('campaigns.json')

classifier = Classifier(user, campaigns)

if classifier.fitting_campaigns:
    print('Fitting campaigns:')
    for fitting_campaign in classifier.fitting_campaigns:
        print('   ', fitting_campaign, '- fitness:', fitting_campaign.evaluate_user(user))

    print()

    print('Best campaign:', classifier.get_best_campaign())
else:
    print('User does not fit any campaign')


