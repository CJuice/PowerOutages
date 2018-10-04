"""

"""
import requests


class WebFunctionality:

    @staticmethod
    def make_web_request(uri):
        try:
            response = requests.get(uri)
        except Exception as e:  # TODO: Refine exception handling
            print(e)
            exit()
        else:
            return response

