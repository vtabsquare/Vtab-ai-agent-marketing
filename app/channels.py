from .integrations import Channel

def get_channels(social_keys, selected_platforms):
    return [Channel(platform, social_keys) for platform in selected_platforms]
