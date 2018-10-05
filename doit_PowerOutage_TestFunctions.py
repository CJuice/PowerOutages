
def check_metadata_uri_presence_against_key_presence(obj_dict):
    for key, obj in obj_dict.items():

        if "BGE" in obj.abbrev:
            print(f"Skip: {obj.metadata_feed_uri} \ {obj.metadata_key}")

        elif obj.metadata_feed_uri == "NA" and obj.metadata_key is None:
            print(f"Satisfactory: {obj.metadata_feed_uri} \ {obj.metadata_key}")
        elif  obj.metadata_feed_uri != "NA" and obj.metadata_key is not None and len(obj.metadata_key.strip()) > 0:
            print(f"Satisfactory: {obj.metadata_feed_uri} \ {obj.metadata_key}")
        else:
            print(f"Unsatisfactory: {key} metadata uri vs key : {obj.metadata_feed_uri} \ {obj.metadata_key}\n\t{obj.metadata_feed_response.text}")
