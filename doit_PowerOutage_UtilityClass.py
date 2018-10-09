import json


class Utility:

    @staticmethod
    def write_to_file(file, content):
        with open(file, 'w') as file_handler:
            file_handler.write(json.dumps(content))
        print(f"{file} written.")
        return
