import requests

current_song_payload = '''{{
  live(station: {radio}) {{
	show {{
	  id
	  ... on DiffusionStep {{
		id
		diffusion {{
		  id
		  title
		  standFirst
		  url
		  published_date
		  podcastEpisode {{
			id
			title
			url
			playerUrl
			created
			duration
		  }}
		}}
	  }}
	  ... on BlankStep {{
		id
		title
	  }}
	}}
	program {{
	  id
	  ... on DiffusionStep {{
		id
		diffusion {{
		  id
		  title
		  standFirst
		  url
		  published_date
		  podcastEpisode {{
			id
			title
			url
			playerUrl
			created
			duration
		  }}
		}}
	  }}
	  ... on BlankStep {{
		id
		title
	  }}
	}}
	song {{
	  id
	  start
	  end
	  track {{
		id
		title
        authors
        composers
        mainArtists
        performers
        productionDate
	  }}
	}}
  }}
}}'''

class RadioFranceCrawler():
    def __init__(self, homeassistant, api_key, output_entities):
        self.homeassistant = homeassistant
        self.api_key = api_key
        self.output_entities = output_entities

    def start(self):
        self.update()

    def stop(self):
        pass

    def update(self):
        ret = requests.post(
            'https://openapi.radiofrance.fr/v1/graphql/',
            headers={'x-token': self.api_key},
            json={'query': current_song_payload.format(**{'radio':self.RADIO})}
        )
        if ret.ok:
            try:
                performers = ' / '.join(ret.json()['data']['live']['song']['track']['performers'])
            except:
                performers = 'Error'

            try:
                title = ret.json()['data']['live']['song']['track']['title']
            except:
                title = 'Error'

        else:
            performers = 'Error'
            title = 'Error'

        self.homeassistant.log(f'performers: {performers}')
        self.homeassistant.log(f'title: {title}')
        if 'current' in self.output_entities:
            entity_current = self.homeassistant.get_entity(self.output_entities['current'])
            entity_current.set_state(f'{performers}\n{title}')

            self.homeassistant.set_state('sensor.radio_live', 'lol', attributes={'current_artist': f'{performers}', 'current_title': f'{title}'})
            # {{ states_attr('sensor.radio_live', 'current_artist') }}

class FIPCrawler(RadioFranceCrawler):
    RADIO = 'FIP'

