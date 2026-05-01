import requests
import time

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

        self.previous = {
            'artist': 'Unknown',
            'title': 'Unknown',
        }
        self.current = {
            'artist': 'Unknown',
            'title': 'Unknown',
        }

    def start(self):
        self.update()

    def stop(self):
        pass

    def update(self, **kwargs):
        self.previous = self.current.copy()
        ret = requests.post(
            'https://openapi.radiofrance.fr/v1/graphql/',
            headers={'x-token': self.api_key},
            json={'query': current_song_payload.format(**{'radio':self.RADIO})}
        )
        if ret.ok:
            try:
                self.current['artist'] = ' / '.join(ret.json()['data']['live']['song']['track']['performers'])
            except:
                self.homeassistant.log('Failed to compute performers', level='WARNING')
                self.current['artist'] = 'Error'

            try:
                track = ret.json()['data']['live']['song']['track']
                self.current['title'] = f"{track['title']} ({track['productionDate']})"
            except:
                self.homeassistant.log('Failed to compute title', level='WARNING')
                self.current['title'] = 'Error'

            try:
                # Compute time to next update
                now = int(time.time())
                start = ret.json()['data']['live']['song']['start']
                end = ret.json()['data']['live']['song']['end']
                self.homeassistant.log(f'now: {now}, start: {start}, end:{end}')

                # Looks like the server in 40s late with me...
                next_song_in = end - now + 40
            except:
                self.homeassistant.log('Failed to compute time to next fetch', level='WARNING')
                next_song_in = 120

        else:
            self.current['artist'] = 'Error'
            self.current['title'] = 'Error'
            next_song_in = 120

        self.homeassistant.log(f'Artist: {self.current["artist"]}')
        self.homeassistant.log(f'Title: {self.current["title"]}')
        self.homeassistant.log(f'next_in: {next_song_in}')

        self.homeassistant.set_state('sensor.radio_live', '', attributes={
                'current_artist': self.current['artist'],
                'current_title': self.current['title'],
                'previous_artist': self.previous['artist'],
                'previous_title': self.previous['title'],
            }
        )

        self.homeassistant.run_in(self.update, next_song_in)


class FIPCrawler(RadioFranceCrawler):
    RADIO = 'FIP'

