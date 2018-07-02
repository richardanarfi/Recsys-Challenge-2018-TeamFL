import sys
import json
import string
import datetime
import os

output_file = open("mpd_dataset.txt", "w", encoding='raw_unicode_escape')
#uniquePlaylists = open("challenge_playlists_unique.txt", "w", encoding='raw_unicode_escape')
#uniqueTracks = open("challenge_tracks_unique.txt", "w", encoding='raw_unicode_escape')
optional_playlist_fields = ["name"]
min_tracks_per_playlist = 5
max_tracks_per_playlist = 250
min_artists_per_playlist = 3
min_albums_per_playlist = 2
max_files_for_quick_processing = 10
#latest_add_ts = int(datetime.datetime(2017, 11, 1).strftime('%s')) * 1000
pids = set()
unique_playlists = set()
unique_tracks = set()

#inputFile = open('mpd.txt')

artist_names = {}
album_names = {}
track_names = {}

gstats = {
    'errors': 0
}


def process_mpd(path):
    count = 0
    #check_challenge_set()
    filenames = os.listdir(path)
    for filename in sorted(filenames):
        if filename.startswith("mpd.slice.") and filename.endswith(".json"):
            fullpath = os.sep.join((path, filename))
            f = open(fullpath)
            js = f.read()
            f.close()
            slice = json.loads(js)
            process_info(slice['info'])
            for playlist in slice['playlists']:
                #count += 1
                #print(count)
                #unique_playlists.add(playlist['name'].replace('+', '').replace('~', '').replace('<', '').replace('>', '').replace('=', '').replace('?', '').replace(':', '').replace(';', '').replace('\"', '').replace('\'', '').replace('.', '').replace('_', '').replace('#', '').replace('!', '').replace('@', '').replace('-', '').replace('/', '').replace('&', '').replace('$', '').replace('{', '').replace('}', '').replace('(', '').replace(')', '').replace('^', '').replace('%', '').replace('*', '').replace(',', '').replace(' ', ''))
                #print(playlist.items())
                for p_name, val in playlist.items():
                    if p_name in optional_playlist_fields:
                        #print(playlist['name'])
                        #val = playlist['name']
                        #print(val)
                        #output_file.write('#')
                        output_file.write(playlist['name'].replace('+', '').replace('~', '').replace('<', '').replace('>', '').replace('=', '').replace('?', '').replace(':', '').replace(';', '').replace('\"', '').replace('\'', '').replace('.', '').replace('_', '').replace('#', '').replace('!', '').replace('@', '').replace('-', '').replace('/', '').replace('&', '').replace('$', '').replace('{', '').replace('}', '').replace('(', '').replace(')', '').replace('^', '').replace('%', '').replace('*', '').replace(',', '').replace(' ', ''))
                        #output_file.write('#')
                        output_file.write(',')
                #n_tracks = playlist['num_samples']

                for track in playlist['tracks']:
                    track_uri = track['track_uri']
                    #unique_tracks.add(track['track_uri'])
                    #uniqueTracks.write(track_uri)
                    #uniqueTracks.write('\n')
                    output_file.write(track_uri)
                    output_file.write(',')
                output_file.write('\n')
            #for playlist in slice['playlists']:
                #for pid in playlist['tracks']:
                #    print(playlist['pid'])
                #print(playlist)

                process_playlist(playlist)
                #print(count)
            count += 1
            print(count)
            if quick and count > max_files_for_quick_processing:
                break

    show_summary()
    #check_challenge_set()


def show_summary():
    tassert(len(pids) == 1000000, "mismatched pids %d %d", len(pids), 1000000)
    missing = set()
    for pid in range(0, 1000000):
        if pid not in pids:
            print(pid)
            missing.add(pid)
    
    tassert(len(missing) == 0, "missing %d pids", len(missing))

    for k, v in gstats.items():
        print(k, v)


required_fields = set(['name', 'collaborative', 'pid', 'modified_at', 'num_albums', 'num_tracks', 'num_followers',
                       'num_tracks', 'num_edits', 'duration_ms', 'num_artists', 'tracks'])
optional_fields = set(['description'])

required_track_fields = set(
    ['pos', 'artist_name', 'artist_uri', 'album_uri', 'album_name', 'track_uri', 'track_name', 'duration_ms'])


def process_playlist(playlist):
    tassert(playlist['pid'] not in pids, "duplicate pid %d", playlist['pid'])
    pids.add(playlist['pid'])
    #unique_playlists.add(playlist['name'])

    tassert(len(playlist['name']) > 0, "zero length playlist title")
    tassert(len(playlist['tracks']) >= min_tracks_per_playlist, "min tracks per playlist < %d", min_tracks_per_playlist)

    for field in playlist:
        tassert(field in required_fields or field in optional_fields, "extra field %s", field)

    for field in required_fields:
        tassert(field in playlist, "missing field %s", field)

    tassert(playlist['num_followers'] >= 1, "too few followers %d", playlist['num_followers'])
    tassert(playlist['num_edits'] > 0, "too few edits %d", playlist['num_edits'])
    #tassert(playlist['modified_at'] <= latest_add_ts, "modified_at too late %d", playlist['modified_at'])

    albums = set()
    artists = set()

    total_duration = 0
    for i, track in enumerate(playlist['tracks']):

        for field in track:
            tassert(field in required_track_fields, "extra track field %s", field)

        for field in required_track_fields:
            tassert(field in track, "missing track field %s", field)

        tassert(i == track['pos'], "out of order %d %d", i, track['pos'])
        artists.add(track['artist_uri'])
        albums.add(track['album_uri'])
        #unique_tracks.add(track['track_uri'])
        total_duration += track['duration_ms']

        if track['artist_uri'] not in artist_names:
            artist_names[track['artist_uri']] = track['artist_name']
        tassert(track['artist_name'] == artist_names[track['artist_uri']], 'mismatch artist name %s %s',
                track['artist_name'], artist_names[track['artist_uri']])

        if track['album_uri'] not in album_names:
            album_names[track['album_uri']] = track['album_name']
        tassert(track['album_name'] == album_names[track['album_uri']], 'mismatch album name %s %s',
                track['album_name'], album_names[track['album_uri']])

        if track['track_uri'] not in track_names:
            track_names[track['track_uri']] = track['track_name']
        tassert(track['track_name'] == track_names[track['track_uri']], 'mismatch track name %s %s',
                track['track_name'], track_names[track['track_uri']])

        tassert(is_track_uri(track['track_uri']), "invalid track uri %s", track['track_uri'])
        tassert(is_album_uri(track['album_uri']), "invalid album uri %s", track['album_uri'])
        tassert(is_artist_uri(track['artist_uri']), "invalid artst uri %s", track['artist_uri'])

    tassert(len(artists) >= min_artists_per_playlist, 'too few artists %d', len(artists))
    tassert(len(albums) >= min_albums_per_playlist, 'too few albums %d', len(albums))
    tassert(len(albums) == playlist['num_albums'], 'nalbum mismatch %d %d', len(albums), playlist['num_albums'])
    tassert(len(artists) == playlist['num_artists'], 'nartist mismatch %d %d', len(artists), playlist['num_artists'])
    tassert(len(playlist['tracks']) == playlist['num_tracks'], 'ntracks mismatch %d %d', len(playlist['tracks']),
            playlist['num_tracks'])
    tassert(total_duration == playlist['duration_ms'], "mismiatch duration %d %d", total_duration,
            playlist['duration_ms'])


required_info_fields = ['generated_on', 'slice', 'version']


def process_info(info):
    for field in info:
        tassert(field in required_info_fields, "extra info field %s", field)

    for field in required_info_fields:
        tassert(field in info, "missing info field %s", field)


def is_track_uri(uri):
    return uri.startswith("spotify:track:")


def is_album_uri(uri):
    return uri.startswith("spotify:album:")


def is_artist_uri(uri):
    return uri.startswith("spotify:artist:")


def tassert(condition, fmtstring, *args):
    if not condition:
        gstats['errors'] += 1
        print(fmtstring % args)


if __name__ == '__main__':
    path = sys.argv[1]
    quick = False
    if len(sys.argv) > 2 and sys.argv[2] == '--quick':
        quick = True
    process_mpd(path)
    #uniqueTracks.write(str(unique_tracks))
    #uniqueTracks.write('\n')
    #uniquePlaylists.write(str(unique_playlists))
    #uniquePlaylists.write('\n')
    #print (len(unique_tracks))
