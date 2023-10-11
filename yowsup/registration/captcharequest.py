from random import randint

from yowsup.common.http.warequest import WARequest
from yowsup.common.http.waresponseparser import JSONResponseParser


class WACaptchaRequest(WARequest):
    def __init__(self, captcha_code, config):
        """
        :param captcha_code:
        :type captcha_code: str
        :param config:
        :type config: yowsup.config.v1.config.Config
        """
        super(WACaptchaRequest, self).__init__(config)

        self.type = "GET"
        self.addParam("audio_button_tap_count", 0)
        time_until_first_key_tap = randint(2000, 3000)
        time_until_code_submit = time_until_first_key_tap + randint(1000, 2000)
        self.addParam("time_until_first_key_tap", time_until_first_key_tap)
        self.addParam("time_until_code_submit", time_until_code_submit)
        self.addParam("refresh_button_tap_count", 0)
        self.addParam("fraud_checkpoint_code", captcha_code)

        self.url = "v.whatsapp.net/v2/captcha_verify"

        self.pvars = ["status", "reason", "email_otp_eligible", "flash_type", "login", "sms_length", "sms_wait"] +\
                    ["voice_length", "voice_wait", "wa_old_eligible"]
        self.setParser(JSONResponseParser())

    def send(self, parser=None, encrypt=True, preview=False, proxy=None):
        super(WACaptchaRequest, self).removeParam("mistyped")
        res = super(WACaptchaRequest, self).send(parser, encrypt=encrypt, preview=preview, proxy=proxy)
        return res
