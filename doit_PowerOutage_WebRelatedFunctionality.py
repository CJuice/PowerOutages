"""

"""
import requests


class WebFunctionality:

    @staticmethod
    def make_web_request(uri, payload=None, style="GET", headers=None):
        # NOTE: In requests module, pass dict directly using the json parameter and it will be encoded automatically
        #   If use data= then must use json.dumps(payload) before passing it in
        try:
            return {"GET": requests.get(url=uri, params=payload),
                    "POST_data": requests.post(url=uri, data=payload, headers=headers),
                    "POST_json": requests.post(url=uri, json=payload, headers=headers),
                    }.get(style)
        except KeyError as ke:
            message = f"{style} not yet supported"
            print(message, ke)
            return message

    # @staticmethod
    # def make_web_request(uri):
    #     try:
    #         response = requests.get(uri)
    #     except Exception as e:  # TODO: Refine exception handling
    #         print(e)
    #         exit()
    #     else:
    #         return response

