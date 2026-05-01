from appdaemon.adapi import ADAPI
from appdaemon.plugins.hass import Hass

import radiofrance

class RadioCurrentSong(Hass):
    CRAWLERS = {
        'FIP': radiofrance.FIPCrawler,
    }

    def initialize(self):
        self.init_done = False
        self.api_key = self.args['api_key']
        self.current_crawler = None

        self.listen_state(self.current_radio_changed_cb, 'sensor.current_radio')
        self.try_init()
        # current_radio = self.get_entity('sensor.current_radio')
        # self.update_current_crawler(current_radio.state)
        # self.call_service(
        #     'notify/mobile_app_oneplus_a6010',
        #     title='TITLE',
        #     message='From AppDaemon !!',
        # )

    def try_init(self, **kwargs):
        if self.init_done:
            return

        current_radio = self.get_state('sensor.current_radio')

        if current_radio not in (None, "unknown", "unavailable"):
            self.init_done = True
            self.update_current_crawler(current_radio)
        else:
            self.run_in(self.try_init, 1)


    def current_radio_changed_cb(self, entity, attribute, old, new, **kwargs):
        self.log(f'Current radio changed from {old} to {new}')
        self.update_current_crawler(new)

    def update_current_crawler(self, current_radio):
        if self.current_crawler:
            self.current_crawler.stop()

        crawler_class = self.CRAWLERS.get(current_radio)

        if crawler_class:
            self.current_crawler = crawler_class(
                homeassistant=self,
                api_key=self.api_key,
                output_entities={
                    'current':'sensor.fipcurrent',
                },
            )
            self.current_crawler.start()
        else:
            self.current_crawler = None

