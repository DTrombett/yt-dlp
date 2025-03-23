from .common import InfoExtractor
from ..utils import clean_html, int_or_none, str_or_none, url_or_none
from ..utils.traversal import traverse_obj


class DiFmIE(InfoExtractor):
    IE_NAME = 'di.fm'
    _VALID_URL = r'https?://(?:www\.)?di\.fm/shows/(?P<show>[^/]+)/episodes/(?P<episode>\d+)'
    _TESTS = [{
        'url': 'https://di.fm/shows/airwaves-progressions-radio/episodes/047',
        'md5': '71b2fb14dc20d8077c73b1976f1056fe',
        'info_dict': {
            'id': '174775',
            'ext': 'mp4',
            'display_id': '047',
            'title': 'Progressions 047 (06 January 2024)',
            'like_count': int,
            'dislike_count': int,
            'duration': 7267,
            'thumbnail': 'http://cdn-images.audioaddict.com/8/2/e/d/5/4/82ed542747238a1b063fda3e22f44264.png',
            'artists': ['Airwave'],
            'episode': 'Progressions 047 (06 January 2024)',
            'episode_id': '3086190',
            'series': 'Airwave\'s Progressions Radio',
            'series_id': 'airwaves-progressions-radio',
        },
    }, {
        'url': 'https://www.di.fm/shows/global-dj-broadcast/episodes/2025-03-20',
        'md5': 'ba050e1124e9b349e3795b36e1e0856f',
        'info_dict': {
            'id': '188340',
            'ext': 'mp4',
            'display_id': '2025-03-20',
            'title': 'Global DJ Broadcast (20 March 2025) with guest BT',
            'like_count': int,
            'dislike_count': int,
            'duration': 7261,
            'thumbnail': 'http://cdn-images.audioaddict.com/a/2/b/2/b/8/a2b2b8b93f24bc8ebe57c3f421a33015.png',
            'artists': ['Markus Schulz'],
            'episode': 'Global DJ Broadcast (20 March 2025) with guest BT',
            'episode_id': '3112886',
            'series': 'Global DJ Broadcast',
            'series_id': 'global-dj-broadcast',
        },
    }]

    def _real_extract(self, url):
        show, episode = self._match_valid_url(url).group('show', 'episode')
        video_id = f'{show}-{episode}'
        webpage = self._download_webpage(url, video_id, impersonate=True)
        details = self._search_json(r'"EpisodeDetail.LayoutEngine",', webpage, 'episode details', video_id)
        data = traverse_obj(details, ('episode', 'tracks', 0, {
            'episode_id': ('id', {str_or_none}),
            'duration': ('length', {int_or_none}),
            'title': ('title', {str}),
            'episode': ('title', {str}),
            'artists': ('artists', ..., 'name', {str}),
            'thumbnail': ('asset_url', {url_or_none}),
            'like_count': ('votes', 'up', {int_or_none}),
            'dislike_count': ('votes', 'down', {int_or_none}),
            'formats': ('content', 'assets', ..., {
                'url': ('url', {clean_html}),
                'format_id': ('content_format_id', {str_or_none}),
                'filesize': ('size', {int_or_none}),
            }),
        }))

        for f in data['formats']:
            f['vcodec'] = 'none'
            f['acodec'] = 'aac'
        return {
            'id': str(details['episode']['id']),
            'display_id': traverse_obj(details, ('episode', 'slug')),
            'series_id': traverse_obj(details, ('show', 'slug')),
            'series': traverse_obj(details, ('show', 'name', {clean_html})),
            **data,
        }
