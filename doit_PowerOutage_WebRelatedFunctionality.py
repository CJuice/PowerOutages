"""
Module containing WebFunctionality class for web interaction
"""
import requests


class WebFunctionality:
    """
    Static class at time of implementation, contains make_web_request() for use by all providers in web transactions
    """
    @staticmethod
    def make_web_request(uri, payload=None, style="GET", headers=None):
        """
        Static method available to all provider classes for use in making web requests
        NOTE: In requests module, pass dict directly using the json parameter and it will be encoded automatically
           If use data= then must use json.dumps(payload) before passing it in
        :param uri: web path to which to make request
        :param payload: payload, if present, to pass in request
        :param style: style of the request, example: GET POST etc...
        :param headers: request headers
        :return: response, unless exception and then message returned
        """

        try:
            return {"GET": requests.get(url=uri, params=payload),
                    "POST_data": requests.post(url=uri, data=payload, headers=headers),
                    "POST_json": requests.post(url=uri, json=payload, headers=headers),
                    }.get(style)
        except KeyError as ke:
            message = f"{style} not yet supported"
            print(message, ke)
            return message

