"""Video assets and timeline mapping for replay, never navigation inputs."""
import base64
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading

_LOCK = threading.Lock()
_BUILDING = set()


def read_media(folder):
    path = Path(folder) / 'media' / 'manifest.json'
    if not path.exists():
        return {'version': 1, 'streams': [], 'state': 'no_recorded_windows'}
    return json.loads(path.read_text())


def update_media(folder, **fields):
    """One writer process owns the manifest while recording; atomic readers."""
    directory = Path(folder) / 'media'
    directory.mkdir(exist_ok=True)
    data = read_media(folder)
    data.update(fields)
    temporary = directory / 'manifest.json.tmp'
    temporary.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2))
    temporary.replace(directory / 'manifest.json')
    return data


def media_path(folder, name):
    """Permit only video files inside this selected recording's media folder."""
    root = (Path(folder) / 'media').resolve()
    path = (root / name).resolve()
    if not path.is_relative_to(root) or path.suffix.lower() not in ('.mp4', '.webm') or not path.is_file():
        raise ValueError('Video not found in the selected recording')
    return path


def byte_range(header, size):
    if size <= 0:
        raise ValueError('Video has no complete bytes yet')
    if not header:
        return 0, size-1, False
    if not header.startswith('bytes=') or ',' in header:
        raise ValueError('Only one byte range is supported')
    start, end = header[6:].split('-', 1)
    if start:
        first = int(start)
        last = min(int(end), size-1) if end else size-1
    else:
        length = int(end)
        if length <= 0:
            raise ValueError('Invalid suffix range')
        first, last = max(0, size-length), size-1
    if not 0 <= first <= last < size:
        raise ValueError('Requested range is outside the video')
    return first, last, True


def camera_groups(folder):
    groups = {}
    path = Path(folder) / 'perception.jsonl'
    if not path.exists():
        return groups
    with path.open() as stream:
        for line in stream:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if (row.get('kind') != 'camera' or row.get('source') not in ('raw', 'detection')
                    or not isinstance(row.get('epoch'), int)
                    or not isinstance(row.get('t'), (int, float)) or not math.isfinite(row['t'])
                    or not str(row.get('image', '')).startswith('data:image/jpeg;base64,')):
                continue
            groups.setdefault((row['epoch'], row['source']), []).append(row)
    for key, rows in groups.items():
        # No future epoch may be concatenated into the preceding epoch's clip.
        groups[key] = sorted({r['t']: r for r in rows}.values(), key=lambda r: r['t'])
    return groups


def build_camera_videos(folder):
    """Encode saved JPEG captures with original simulation-time spacing."""
    folder = Path(folder)
    (folder/'media').mkdir(exist_ok=True)
    data = read_media(folder)
    if data.get('camera_state') == 'ready':
        return data
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        return update_media(folder, camera_state='unavailable', camera_error='Thiếu ffmpeg; camera vẫn phát chuỗi khung hình đã lưu.')
    streams = [s for s in data.get('streams', []) if s.get('kind') != 'camera']
    for (epoch, source), rows in camera_groups(folder).items():
        if not rows:
            continue
        name = f'camera_{source}_epoch{epoch}.mp4'
        output = folder / 'media' / name
        temporary = output.with_suffix('.tmp.mp4')
        with tempfile.TemporaryDirectory(prefix='replay_camera_') as directory:
            work = Path(directory)
            concat = []
            for i, row in enumerate(rows):
                jpeg = base64.b64decode(row['image'].split(',', 1)[1], validate=True)
                (work / f'frame{i:07d}.jpg').write_bytes(jpeg)
                duration = max(.001, rows[i+1]['t']-row['t']) if i+1 < len(rows) else .1
                concat.extend((f"file 'frame{i:07d}.jpg'", f'duration {duration:.9f}'))
            concat.append(f"file 'frame{len(rows)-1:07d}.jpg'")
            (work / 'frames.txt').write_text('\n'.join(concat)+'\n')
            command = [ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'error', '-y',
                       '-f', 'concat', '-safe', '0', '-i', str(work/'frames.txt'),
                       '-vf', 'scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2',
                       '-vsync', 'vfr', '-an', '-c:v', 'libx264', '-threads', '1', '-preset', 'ultrafast',
                       '-crf', '27', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(temporary)]
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        temporary.replace(output)
        streams.append(dict(kind='camera', source=source, epoch=epoch, file=name,
                            t_start=rows[0]['t'], t_end=rows[-1]['t']+.1,
                            frames=len(rows), timebase='simulation',
                            note='Video từ các khung đã ghi; khoảng thiếu ảnh được giữ nguyên, không tạo ảnh mới.'))
    return update_media(folder, streams=streams, camera_state='ready', camera_error=None)


def ensure_camera_videos(folder):
    """Build legacy recordings only after their writer finished, in a worker."""
    folder = Path(folder).resolve()
    state = read_media(folder)
    if state.get('camera_state') in ('ready', 'building', 'recording', 'error') or (state.get('camera_state') == 'unavailable' and not shutil.which('ffmpeg')):
        return state
    status = folder / 'perception_status.json'
    if not status.exists() or not json.loads(status.read_text()).get('writer_finished'):
        return state
    with _LOCK:
        if folder in _BUILDING:
            return state
        _BUILDING.add(folder)
    update_media(folder, camera_state='building')
    def worker():
        try:
            build_camera_videos(folder)
        except Exception as error:
            update_media(folder, camera_state='error', camera_error=str(error)[-500:])
        finally:
            with _LOCK:
                _BUILDING.discard(folder)
    threading.Thread(target=worker, daemon=False).start()
    return read_media(folder)
