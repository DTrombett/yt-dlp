import json

from .common import InfoExtractor
from ..utils import clean_html, int_or_none, str_or_none, url_or_none
from ..utils.traversal import traverse_obj


class DiFmEpisodeIE(InfoExtractor):
    IE_NAME = 'di.fm:episode'
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
            'title': ('title', {str_or_none}),
            'episode': ('title', {str_or_none}),
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
            f.setdefault('vcodec', 'none')
            f.setdefault('acodec', 'aac')
            f.setdefault('ext', 'm4a')
            if f.get('filesize') and data.get('duration'):
                f['tbr'] = f['filesize'] / data['duration'] / 125
        return {
            'id': str(details['episode']['id']),
            'display_id': traverse_obj(details, ('episode', 'slug')),
            'series_id': traverse_obj(details, ('show', 'slug')),
            'series': traverse_obj(details, ('show', 'name', {clean_html})),
            **data,
        }


class DIFmPlaylistIE(InfoExtractor):
    IE_NAME = 'di.fm:playlist'
    _VALID_URL = r'https?://(?:www\.)?di\.fm/playlists/(?P<id>[^/]+)'
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
        playlist_id = self._match_id(url)
        webpage = self._download_webpage(url, playlist_id, impersonate=True)
        playlist_details = self._search_json(r'"PlaylistDetail.LayoutEngine",', webpage, 'playlist details', playlist_id)
        playlist_id = str(playlist_details['playlist']['id'])
        data = traverse_obj(playlist_details, ('playlist', {
            'display_id': ('slug', {str_or_none}),
            'description': ('description', {str_or_none}),
            'title': ('name', {str_or_none}),
            'uploader': ('curator', 'name', {str_or_none}),
            'uploader_id': ('curator', 'slug', {str_or_none}),
            'playlist_count': ('track_count', {int_or_none}),
            'view_count': ('play_count', {int_or_none}),
            'like_count': ('follow_count', {int_or_none}),
            'thumbnails': ('images', {dict.items}, lambda _, v: url_or_none(v[1]), {
                'id': 0,
                'url': (1, {lambda x: x.split('{')[0]}),
            }),
            'tags': ('tags', ..., 'name', {str}),
        }))
        session_key = self._search_json(r'app\.start\(', webpage, 'app details', playlist_id)['user']['session_key']

        def entries():
            while True:
                tracks = self._download_json(f'https://api.audioaddict.com/v1/di/playlists/{playlist_id}/play', playlist_id, 'Downloading playlist tracks', headers={'x-session-key': session_key}, data=b'')['tracks']
                for track in tracks:
                    yield traverse_obj(track, {
                        'artists': ('artists', ..., 'name', {str}),
                        'thumbnail': ('asset_url', {url_or_none}),
                        'title': ('title', {str_or_none}),
                        'id': ('id', {str_or_none}),
                        'duration': ('length', {int_or_none}),
                        'track': ('track', {str_or_none}),
                        'like_count': ('votes', 'up', {int_or_none}),
                        'dislike_count': ('votes', 'down', {int_or_none}),
                        'formats': ('content', 'assets', ..., {
                            'url': ('url', {str}),
                            'format_id': ('content_format_id', {str_or_none}),
                            'filesize': ('size', {int_or_none}),
                            'vcodec': ({lambda _: 'none'}),
                            'acodec': ({lambda _: 'aac'}),
                            'ext': ({lambda _: 'm4a'}),
                            'tbr': ('size', {int_or_none}, {lambda s: s / track['length'] / 125 if track.get('length') else None}),
                        }),
                    })
                    self._download_json('https://api.audioaddict.com/v1/di/listen_history', str(track['id']), 'Marking as listened', headers={'x-session-key': session_key}, data=json.dumps({'track_id': track['id'], 'playlist_id': int(playlist_id)}).encode())
                if tracks['last_tracks']:
                    break
        return self.playlist_result(entries(), playlist_id, **data)
