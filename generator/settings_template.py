import datetime, pytz

# Set to True to enable debugging mode, False to disable. Do not leave on in production!
DEBUG = False

# Default email address for who to contact regarding content in a show.
DEFAULT_EDITORIAL_EMAIL = "editor@example.org"
# Default email address for who to contact regarding technical aspects of the podcast feed.
DEFAULT_TECHNICAL_EMAIL = "it@example.org"
# Name and email for the podcast owner, which will be contacted by iTunes for questions, problems etc.
# regarding the podcasts
OWNER_NAME = "Example Radio"
OWNER_EMAIL = "it@example.org"

# Default short description to use on shows with no description.
DEFAULT_SHORT_FEED_DESCRIPTION = "Podcast from Example Radio"
# Default website to use on shows with no website.
DEFAULT_WEBSITE = "http://example.org"

# Determines whether new episode duration should be calculated by default. Modified by command line options.
FIND_EPISODE_DURATIONS = False

# Determines whether progress information should be printed. Modified by command line options.
QUIET = True


# SHOW SOURCE SETTINGS

SHOW_SOURCE = {
    # Base URL for the Radio Rest API (without trailing slash). Example: "http://example.org/v1"
    'RADIO_REST_API_URL': "URL HERE",

    # Username for authenticating with the Radio Rest API
    'RADIO_REST_API_USERNAME': "USERNAME HERE",

    # Password for authenticating with the Radio Rest API
    'RADIO_REST_API_PASSWORD': "PASSWORD HERE",
}


# EPISODE SOURCE SETTINGS

EPISODE_SOURCE = {
    # Base URL for the Radio Rest API (without trailing slash). Example: "http://example.org/v1"
    # Reuse value from SHOW_SOURCE
    'RADIO_REST_API_URL': SHOW_SOURCE['RADIO_REST_API_URL'],
}


# METADATA SOURCE SETTINGS

METADATA_SOURCE = {

    # CHIMERA SETTINGS
    'CHIMERA': {
        # Base URL for CHIMERA RADIO API (without trailing slash). Example: "http://example.org/radio/api"
        'API_URL': "URL",

        # Episodes from this date until END_DATE will get metadata from Chimera.
        # Remember that it is set to UTC timezone, not CET or CEST.
        # datetime.datetime(year, month, day, hour, minute, tzinfo=pytz.utc) or None
        'START_DATE': datetime.datetime(2016, 4, 12, 0, 0, tzinfo=pytz.utc),

        # Episodes before this date and time but after START_DATE will get metadata from Chimera.
        # Set to None to set no boundary.
        # datetime.datetime(year, month, day, hour, minute, tzinfo=pytz.utc) or None
        'END_DATE': None,

        # Add the URL of episodes you want to bypass Chimera to this set. Do this with episodes that you want to publish
        # even though they aren't found in Chimera.
        'BYPASS': {
            "URL of episode to bypass",
            "another URL for an episode to bypass"
        },
    },

    # RADIOREVOLT.NO SETTINGS
    # TODO: Implement metadata source for RadioRevolt.no
    'RADIO_REVOLT': {
        # Base URL for RADIO REVOLT API (without trailing slash).
        'API_URL': "URL",

        # Episodes from this date or newer will get metadata from RadioRevolt.no.
        # datetime.date(year, month, day) or None
        'START_DATE': datetime.date(2000, 1, 1),
    },

}
