from appdaemon.adapi import ADAPI
from appdaemon.plugins.hass import Hass

import requests

payload = '''{
  live(station: FIP) {
	show {
	  id
	  ... on DiffusionStep {
		id
		diffusion {
		  id
		  title
		  standFirst
		  url
		  published_date
		  podcastEpisode {
			id
			title
			url
			playerUrl
			created
			duration
		  }
		}
	  }
	  ... on BlankStep {
		id
		title
	  }
	}
	program {
	  id
	  ... on DiffusionStep {
		id
		diffusion {
		  id
		  title
		  standFirst
		  url
		  published_date
		  podcastEpisode {
			id
			title
			url
			playerUrl
			created
			duration
		  }
		}
	  }
	  ... on BlankStep {
		id
		title
	  }
	}
	song {
	  id
	  start
	  end
	  track {
		id
		title
        authors
        composers
        mainArtists
        performers
        productionDate
	  }
	}
  }
}'''


class RadioCurrentSong(Hass):
    def initialize(self):
        self.api_key = self.args['api_key']
        current_radio = self.get_entity('sensor.current_radio')
        if current_radio.get_state() == 'FIP':
            self.push_fip_song()
        current_radio.listen_state(self.current_radio_changed_cb)
        # self.call_service(
        #     'notify/mobile_app_oneplus_a6010',
        #     title='TITLE',
        #     message='From AppDaemon !!',
        # )
        # self.set_state(
        #     "sensor.test_appdaemon",
        #     state="World",
        #     attributes={
        #         "friendly_name": "Test AppDaemon"
        #     }
        # )
    def current_radio_changed_cb(self, entity, attribute, old, new, **kwargs):
        self.log(f'Current radio changed from {old} to {new}')
        if new == 'FIP':
            self.push_fip_song()

    def push_fip_song(self):
        fip_current = self.get_entity('sensor.fipcurrent')
        ret = requests.post('https://openapi.radiofrance.fr/v1/graphql/', headers={'x-token': self.api_key}, json={'query': payload}, verify=False)
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

        fip_current.set_state(f'{performers}\n{title}')


