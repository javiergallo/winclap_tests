# -*- coding: utf-8 -*-
import json

ALL = None
METHUSELAH_AGE = 969  # xD


def evaluate_string(user_value, campaing_value):
    return (0.75 if campaing_value == ALL else
            1.0 if user_value.lower() == campaing_value.lower() else
            0.0)


class Campaign(object):
    def __init__(self, cid, name, gender=ALL,
                 min_age=0, max_age=METHUSELAH_AGE,
                 platform=ALL, connection=ALL):
        self.cid = cid
        self.name = name
        self.gender = gender
        self.min_age = min_age
        self.max_age = max_age
        self.platform = platform
        self.connection = connection

    def evaluate_age(self, age):
        age_avg = (self.max_age + self.min_age) / 2.0
        age_dev = age_avg - self.min_age
        return max(0.0, 1.0 - abs(age - age_avg) / age_dev)

    def evaluate_gender(self, gender):
        return evaluate_string(gender, self.gender)

    def evaluate_platform(self, platform):
        return evaluate_string(platform, self.platform)

    def evaluate_connection(self, connection):
        return evaluate_string(connection, self.connection)

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
                campaign.evaluate_gender(self.gender) and
                campaign.evaluate_platform(self.platform) and
                campaign.evaluate_connection(self.connection))

    def evaluate_fitness(self, campaign, weights):
        w = weights
        return (
            w['age'] * campaign.evaluate_age(self.age) +
            w['gender'] * campaign.evaluate_gender(self.gender) +
            w['platform'] * campaign.evaluate_platform(self.platform) +
            w['connection'] * campaign.evaluate_connection(self.connection)
        )


class Classifier(object):
    WEIGHTS = {
        'age': 0.2,
        'gender': 0.3,
        'platform': 0.25,
        'connection': 0.25
    }

    _fitting_campaigns = None
    _fitness_data = None

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

    @property
    def fitness_data(self):
        if self._fitness_data is None:
            self._fitness_data = {
                campaign: self.user.evaluate_fitness(campaign, self.WEIGHTS)
                for campaign in self.fitting_campaigns
            }
        return self._fitness_data

    def get_best_campaign(self):
        return max(
            self.fitting_campaigns,
            key=lambda campaign: self.fitness_data[campaign]
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

if classifier.fitness_data:
    print('Fitting campaigns:')
    for campaign, fitness in classifier.fitness_data.items():
        print('   {campaign} - fitness: {fitness}'.format(campaign=campaign,
                                                          fitness=fitness))

    print()

    print('Best campaign:', classifier.get_best_campaign())
else:
    print('User does not fit any campaign')
