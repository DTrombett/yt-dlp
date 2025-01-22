
from .common import InfoExtractor
from ..utils import (
    float_or_none,
    int_or_none,
    js_to_json,
    url_or_none,
)
from ..utils.traversal import traverse_obj


class XiaoHongShuIE(InfoExtractor):
    _VALID_URL = r'https?://www\.xiaohongshu\.com/(?:explore|discovery/item)/(?P<id>[\da-f]+)'
    IE_DESC = '小红书'
    _TESTS = [{
        'url': 'https://www.xiaohongshu.com/explore/6786df34000000001901d188',
        'md5': '',
        'info_dict': {
            'id': '6786df34000000001901d188',
            'ext': 'mp4',
        },
    }, {
        'url': 'https://www.xiaohongshu.com/explore/6411cf99000000001300b6d9',
        'md5': '2a87a77ddbedcaeeda8d7eae61b61228',
        'info_dict': {
            'id': '6411cf99000000001300b6d9',
            'ext': 'mp4',
            'uploader_id': '5c31698d0000000007018a31',
            'description': '#今日快乐今日发[话题]# #吃货薯看这里[话题]# #香妃蛋糕[话题]# #小五卷蛋糕[话题]# #新手蛋糕卷[话题]#',
            'title': '香妃蛋糕也太香了吧🔥不需要卷❗️绝对的友好',
            'tags': ['今日快乐今日发', '吃货薯看这里', '香妃蛋糕', '小五卷蛋糕', '新手蛋糕卷'],
            'duration': 101.726,
            'thumbnail': r're:https?://sns-webpic-qc\.xhscdn\.com/\d+/[a-z0-9]+/[\w]+',
        },
    }, {
        'url': 'https://www.xiaohongshu.com/discovery/item/674051740000000007027a15?xsec_token=CBgeL8Dxd1ZWBhwqRd568gAZ_iwG-9JIf9tnApNmteU2E=',
        'info_dict': {
            'id': '674051740000000007027a15',
            'ext': 'mp4',
            'title': '相互喜欢就可以了',
            'uploader_id': '63439913000000001901f49a',
            'duration': 28.073,
            'description': '#广州[话题]# #深圳[话题]# #香港[话题]# #街头采访[话题]# #是你喜欢的类型[话题]#',
            'thumbnail': r're:https?://sns-webpic-qc\.xhscdn\.com/\d+/[\da-f]+/[^/]+',
            'tags': ['广州', '深圳', '香港', '街头采访', '是你喜欢的类型'],
        },
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)
        initial_state = self._search_json(
            r'window\.__INITIAL_STATE__\s*=', webpage, 'initial state', display_id, transform_source=js_to_json)

        note_info = traverse_obj(initial_state, ('note', 'noteDetailMap', display_id, 'note'))
        streams = traverse_obj(note_info, ('video', 'media', 'stream', ..., ...))

        formats = []
        for stream in streams:
            format_info = traverse_obj(stream, {
                'fps': ('fps', {int_or_none}),
                'width': ('width', {int_or_none}),
                'height': ('height', {int_or_none}),
                'vcodec': ('videoCodec', {str}),
                'acodec': ('audioCodec', {str}),
                'abr': ('audioBitrate', {int_or_none(scale=1000)}),
                'vbr': ('videoBitrate', {int_or_none(scale=1000)}),
                'audio_channels': ('audioChannels', {int_or_none}),
                'tbr': ('avgBitrate', {int_or_none(scale=1000)}),
                'format': ('qualityType', {str}),
                'filesize': ('size', {int_or_none}),
                'duration': ('duration', {float_or_none(scale=1000)}),
            })

            formats.append({
                'url': stream['masterUrl'],
                'format_id': str(stream['streamType']),
                'quality': 0,
                **format_info,
            })
            for u in stream.get('backupUrls') or []:
                formats.append({'format_id': f"{stream['streamType']}-backup", 'url': u, **format_info})

        thumbnails = []
        for image_info in traverse_obj(note_info, ('imageList', ...)):
            thumbnail_info = traverse_obj(image_info, {
                'height': ('height', {int_or_none}),
                'width': ('width', {int_or_none}),
            })
            for thumb_url in traverse_obj(image_info, (('urlDefault', 'urlPre'), {url_or_none})):
                thumbnails.append({
                    'url': thumb_url,
                    **thumbnail_info,
                })

        return {
            'id': display_id,
            'formats': formats,
            'thumbnails': thumbnails,
            **traverse_obj(note_info, {
                'title': ('title', {str}),
                'description': ('desc', {str}),
                'tags': ('tagList', ..., 'name', {str}),
                'uploader_id': ('user', 'userId', {str}),
                'timestamp': ('time', {int_or_none}),
                'modified_timestamp': ('lastUpdateTime', {int_or_none}),
                'channel': ('user', 'nickname', {str}),
            }),
        }
