from flask import redirect, url_for, abort, make_response, Flask

from feed_utils.no_episodes_error import NoEpisodesError
from feed_utils.no_such_show_error import NoSuchShowError
from feed_utils.populate import run_episode_pipeline, run_show_pipeline
from feed_utils.show import Show


def xslt_url():
    return url_for('static', filename="style.xsl")


def output_all_feed(all_episodes_settings, all_episodes_ttl, show_source, episode_source, processors):
    show = Show(id=0, **all_episodes_settings)
    show = run_show_pipeline(show, processors['show']['all_feed'])
    episodes = episode_source.get_all_episodes_list(show_source)
    episodes = run_episode_pipeline(episodes, processors['episode']['web'])
    show.episodes = episodes
    return _prepare_feed_response(show, all_episodes_ttl)


def output_feed(show_name, feed_ttl, completed_ttl_factor, alternate_all_episodes_uri, url_service, show_source, episode_source, processors):
    return output_special_feed(DEFAULT_PIPELINE, show_name, feed_ttl, completed_ttl_factor, alternate_all_episodes_uri, url_service, show_source, episode_source, processors)


# Note: when adding pipelines here, you must also change init_pipelines.py so
# the validation of the configuration includes the new pipeline
ALLOWED_PIPELINES = {
    'web',
    'spotify',
}
DEFAULT_PIPELINE = 'web'


def output_special_feed(pipeline, show_name, feed_ttl, completed_ttl_factor, alternate_all_episodes_uri, url_service, show_source, episode_source, processors):
    if pipeline not in ALLOWED_PIPELINES:
        abort(404, 'Pipeline "{}" not recognized'.format(pipeline))

    if pipeline in processors['show']:
        show_pipeline = pipeline
    else:
        show_pipeline = DEFAULT_PIPELINE

    if pipeline in processors['episode']:
        episode_pipeline = pipeline
    else:
        episode_pipeline = DEFAULT_PIPELINE

    try:
        show, canonical_slug = \
            url_service.get_canonical_slug_for_slug(show_name)
    except NoSuchShowError:
        # Are we perhaps supposed to redirect to /all?
        if show_name.lower() in (name.lower() for name in alternate_all_episodes_uri):
            return redirect(url_for("output_all_feed"))
        else:
            abort(404)
    show_instance = show_source.get_show(show)

    if not show_name == canonical_slug:
        return redirect(url_for_feed(canonical_slug, pipeline))

    populated_show = run_show_pipeline(
        show_instance, processors['show'][show_pipeline]
    )

    is_completed = show_instance.complete
    # VERY IMPORTANT! We don't want Itunes to stop refreshing a show just
    # because it's not running right now, because it might very well return
    # some day. So don't mark any show as completed.
    populated_show.complete = False

    try:
        episodes = episode_source.episode_list(populated_show)
    except NoEpisodesError:
        episodes = []
    populated_episodes = run_episode_pipeline(
        episodes, processors['episode'][episode_pipeline]
    )
    populated_show.episodes = populated_episodes

    if is_completed:
        ttl = round(feed_ttl * completed_ttl_factor)
    else:
        ttl = feed_ttl

    return _prepare_feed_response(populated_show, ttl)


def _prepare_feed_response(show, max_age):
    show.xslt = xslt_url()
    feed = show.rss_str()
    resp = make_response(feed)
    resp.headers['Content-Type'] = 'application/xml'
    resp.cache_control.max_age = max_age
    resp.cache_control.public = True
    return resp


def url_for_feed(slug, pipeline=None):
    if not pipeline or pipeline == DEFAULT_PIPELINE:
        return url_for("output_feed", show_name=slug, _external=True)
    else:
        return url_for(
            "output_special_feed",
            show_name=slug,
            pipeline=pipeline,
            _external=True
        )


def register_feed_routes(app: Flask, settings, get_global):
    def inject_feed_arguments(func):
        def run_func(*args, **kwargs):
            kwargs['feed_ttl'] = settings['caching']['feed_ttl']
            kwargs['completed_ttl_factor'] = settings['caching']['completed_ttl_factor']
            kwargs['alternate_all_episodes_uri'] = settings['all_episodes_show_aliases']
            kwargs['url_service'] = get_global('url_service')
            kwargs['show_source'] = get_global('show_source')
            kwargs['episode_source'] = get_global('episode_source')
            kwargs['processors'] = get_global('processors')
            return func(*args, **kwargs)
        return run_func
    app.add_url_rule("/<show_name>", "output_feed", inject_feed_arguments(output_feed))
    app.add_url_rule("/<pipeline>/<show_name>", "output_special_feed", inject_feed_arguments(output_special_feed))

    def do_output_all_feed():
        return output_all_feed(
            settings['feed']['metadata_all_episodes'],
            settings['caching']['all_episodes_ttl'],
            get_global('show_source'),
            get_global('episode_source'),
            get_global('processors'),
        )
    app.add_url_rule("/all", "output_all_feed", do_output_all_feed)
