#!/usr/bin/env python3
"""按 cue 时间轴给帧序列叠标注，再编码成片。

帧名自带相对毫秒，cue 也用相对毫秒，所以字幕/高亮只会出现在它实际描述的那几帧上，
不存在估算漂移。cue 里的包围盒是录制时从页面实测的，不是目测比例。
"""
import json
import os
import re
import shutil
import subprocess
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from annotate import render  # noqa: E402

ROOT = os.environ.get('DEMO_VIDEO_ROOT', '/tmp/demo-video')
FPS = 30
MAX_HOLD_S = 1.6
MIN_HOLD_S = 0.75        # 每张画面最短停留：低于这个数看起来就是闪
BATCH_STRIDE = 100000    # 每轮录制的帧序号偏移步长，用来把不同轮次区分开
VOICE_LEAD_MS = 150      # 配音前的起手静音，与音轨 adelay 对齐
VOICE_TAIL_MS = 150      # 句末余韵，留够换气又不至于出现空档
CELL_DELTA = 8           # 单格灰度变化超过这个数，才算这一格真的变了
MOVED_RATIO = 0.002      # 变动格占比低于这个数，就当画面没往前走
STATE_WINDOW = 6         # 回看多少帧，判断画面是不是又转回刚才那个状态
SHIMMER_RATIO = 0.50     # 这一帧和近期旧状态的差 低于 和参考帧差 的这个比例，就是两态抖动
SHIMMER_FLOOR = 0.4      # 相邻帧差小于这个数就是真静止，不用管
POINTER_TRAVEL = 0.22    # 激光笔每段里只用这点时间赶路，其余时间停在关键点上

def _ffmpeg():
    """依次找 ffmpeg：环境变量 → imageio_ffmpeg 自带的 → PATH 上的。"""
    if os.environ.get('DEMO_VIDEO_FFMPEG'):
        return os.environ['DEMO_VIDEO_FFMPEG']
    try:
        return subprocess.run(
            [sys.executable, '-c', 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())'],
            capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return shutil.which('ffmpeg') or 'ffmpeg'


FFMPEG = _ffmpeg()


def run(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f'命令失败：{" ".join(cmd[:5])}…\n{proc.stderr[-2000:]}')
    return proc


def frames_of(frames_dir, batch=None):
    """只取单轮录制的帧。

    每轮录制的帧名是 f{全局序号}_{本轮相对毫秒}，序号按轮次加偏移，但毫秒都从 0 重新计。
    多轮录制写进同一个目录时，按毫秒排序会把两轮的画面一比一交错，成片看上去就是
    在两个完全不同的页面之间来回闪——所以宁可报错，也不能默默混着用。
    """
    groups = {}
    for name in sorted(os.listdir(frames_dir)):
        match = re.match(r'f(\d+)_(\d+)\.jpg$', name)
        if not match:
            continue
        index, ms = int(match.group(1)), int(match.group(2))
        groups.setdefault(index // BATCH_STRIDE, []).append((ms, os.path.join(frames_dir, name)))
    if not groups:
        return []
    if batch is None:
        if len(groups) > 1:
            raise SystemExit(
                f'{frames_dir} 里混了 {len(groups)} 轮录制（批次 {sorted(groups)}），'
                '毫秒区间重叠会交错成闪屏；用 KD_BATCH=<批次号> 指定一轮')
        batch = next(iter(groups))
    items = groups.get(batch)
    if not items:
        raise SystemExit(f'{frames_dir} 里没有批次 {batch} 的帧（现有 {sorted(groups)}）')
    items.sort()
    return items


def signature(path):
    """画面的粗指纹。逐字节比对太严，缩到 64x64 灰度足够区分"状态"又不被噪点带偏。"""
    with Image.open(path) as image:
        return image.convert('L').resize((64, 64)).tobytes()


def same_state(a, b):
    """看有多少格真的变了，而不是看平均变了多少。

    取均值会被大片没变的区域摊平：画面上多出一条细线只影响百分之一的格子，
    均值几乎不动，可那恰恰是必须留下的一帧。按格计数就不会漏掉这种小幅动作，
    同时整页跳变（变动格过半）照样判得出来。
    """
    moved = sum(1 for x, y in zip(a, b) if abs(x - y) > CELL_DELTA)
    return moved / len(a) < MOVED_RATIO


TRIM_SILENCE = ('silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,'
                'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse')


def trimmed_voice(src, dst):
    """TTS 片段首尾各自带着半秒静音，照原样拼起来每句之间就多出一秒空档。
    先削到只剩 0.05 秒的呼吸，再拿削完的时长去排镜头长度，间隔才算得准。"""
    run([FFMPEG, '-y', '-loglevel', 'error', '-i', src, '-af', TRIM_SILENCE,
         '-c:a', 'aac', '-b:a', '160k', dst])
    return dst


def duration_of(path):
    proc = subprocess.run([FFMPEG, '-i', path], capture_output=True, text=True)
    match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', proc.stderr)
    if not match:
        return 0.0
    h, m, sec = match.groups()
    return int(h) * 3600 + int(m) * 60 + float(sec)


def readable_ms(subtitle):
    """字幕至少要够读完：中文按每秒 6 字估，再留 1.2 秒余量。"""
    return int(1200 + len(subtitle or '') / 6.0 * 1000)


def cue_at(cues, ms):
    for cue in cues:
        if cue['from'] <= ms < cue['to']:
            return cue
    return None


def build(name, frames_dir, cues_path, out_path, batch=None):
    cues = json.load(open(cues_path, encoding='utf-8'))
    items = frames_of(frames_dir, batch) if os.path.isdir(frames_dir) else []
    if not items and not any(c.get('video') for c in cues):
        raise SystemExit(f'{frames_dir} 没有帧')

    work = os.path.join(ROOT, 'work', name)
    os.makedirs(work, exist_ok=True)

    # 按 cue 分桶：同一个 cue 内部去重，但整段时长由 cue 区间决定——
    # 静止镜头会被去重成一帧，如果还按帧间隔算时长，字幕只闪 1.6 秒就没了，根本读不完。
    buckets = {cue['id']: [] for cue in cues}
    video_ids = {c['id'] for c in cues if c.get('video')}
    for ms, path in items:
        cue = cue_at([c for c in cues if c['id'] not in video_ids], ms)
        if cue is None:
            continue                      # 没有 cue 覆盖的帧不进片，避免出现无字幕的悬空画面
        buckets[cue['id']].append((ms, path))

    plan = []
    timeline = []          # 每个 cue 在成片里占多长，音轨按它对齐
    for cue in cues:
        # 交互镜头走连续视频：从录像里裁一段，不抽稀
        if cue.get('video'):
            voice = os.path.join(ROOT, 'audio', f"{cue['id']}.m4a")
            voice_s = duration_of(voice) if os.path.exists(voice) else 0.0
            spec = {'chip': cue.get('chip'),
                    'highlights': [r if isinstance(r, dict) else {'rect': r} for r in cue.get('rects', [])],
                    'notes': cue.get('notes', []), 'redact': cue.get('redact', []),
                    'subtitle': cue.get('subtitle'),
                    'pointer_path': cue.get('pointer_path')}
            target = (voice_s + VOICE_LEAD_MS / 1000.0 + VOICE_TAIL_MS / 1000.0) if voice_s else None
            done, n = clip_from_video(os.path.join(ROOT, cue['video']),
                                      cue['from'], cue['to'],
                                      os.path.join(work, cue['id']), spec, target_s=target)
            hold = 1.0 / FPS
            for i in range(n):
                plan.append((os.path.join(done, f'{i:06d}.jpg'), hold))
            span = n * hold
            # 硬门禁：画面短于配音就是截断，宁可构建失败也不要出一条话说一半的片子
            if voice_s and span + 0.02 < voice_s + VOICE_LEAD_MS / 1000.0:
                raise SystemExit(
                    f'{cue["id"]}: 画面 {span:.2f}s 装不下配音 {voice_s:.2f}s，会截断')
            timeline.append({'id': cue['id'], 'seconds': span,
                             'voice': voice if voice_s else ''})
            continue

        shots = buckets.get(cue['id']) or []
        if not shots:
            continue
        # 去重不能只比上一帧：右栏助手面板会在两个状态之间来回跳，
        # 只比相邻帧的话 A/B/A/B 里每一帧都"和上一帧不同"，全留下来就是肉眼可见的闪。
        # 只要这一帧回到了最近几帧出现过的状态，就当它没往前走，直接丢掉。
        kept, recent = [], []
        for ms, path in shots:
            sig = signature(path)
            if any(same_state(sig, seen) for seen in recent):
                continue
            recent.append(sig)
            del recent[:-STATE_WINDOW]
            kept.append((ms, path))
        # 镜头时长以配音为准，不再按实拍时长铺：实拍里混着助手打字、页面跳转，
        # 画面长于配音的部分全是静音，连起来听就是一段段断档。
        raw_voice = os.path.join(ROOT, 'audio', f"{cue['id']}.m4a")
        voice = ''
        voice_s = 0.0
        if os.path.exists(raw_voice):
            os.makedirs(os.path.join(work, 'voice'), exist_ok=True)
            voice = trimmed_voice(raw_voice, os.path.join(work, 'voice', f"{cue['id']}.m4a"))
            voice_s = duration_of(voice)
        if voice_s:
            # 字幕就是念出来的这句话，念完就该切。再按"够不够读"去凑时长，
            # 多出来的部分全是句尾静音，一句接一句听着就是断断续续。
            span = int(voice_s * 1000) + VOICE_LEAD_MS + VOICE_TAIL_MS
        else:
            span = max(readable_ms(cue.get('subtitle', '')), 2500)
        voice_ms = int(voice_s * 1000)

        # 右栏助手在持续吐字，每一帧都和上一帧不同，去重去不掉，结果一秒闪五到七张
        # 完全不同的画面。按目标时长限流：每张至少停 MIN_HOLD_S，超出的均匀抽稀。
        budget = max(1, int(span / 1000.0 / MIN_HOLD_S))
        if len(kept) > budget:
            step = len(kept) / budget
            kept = [kept[min(len(kept) - 1, int(i * step))] for i in range(budget)]

        start_len = len(plan)
        hold = (span / 1000.0) / max(len(kept), 1)
        for ms, path in kept:
            out_frame = os.path.join(work, f'{len(plan):06d}.jpg')
            render(path, out_frame, {
                'chip': cue.get('chip'),
                'highlights': [r if isinstance(r, dict) else {'rect': r} for r in cue.get('rects', [])],
                'notes': cue.get('notes', []),
                'redact': cue.get('redact', []),
                'subtitle': cue.get('subtitle'),
            })
            plan.append((out_frame, hold))
        held = sum(h for _, h in plan[start_len:])
        timeline.append({'id': cue['id'], 'seconds': held, 'voice': voice if voice_ms else ''})

    if not plan:
        raise SystemExit(f'{name}: 没有任何帧落在 cue 区间内')
    listing = os.path.join(work, 'concat.txt')
    with open(listing, 'w') as handle:
        for path, hold in plan:
            handle.write(f"file '{path}'\nduration {hold:.3f}\n")
        handle.write(f"file '{plan[-1][0]}'\n")
    silent = os.path.join(work, 'silent.mp4')
    run([FFMPEG, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', listing,
         '-vf', f'fps={FPS},setsar=1,format=yuv420p', '-r', str(FPS),
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-movflags', '+faststart', silent])

    # 每个 cue 的配音铺到它自己的时长上，没有配音的补静音；拼起来正好和画面等长
    pieces = []
    for index, item in enumerate(timeline):
        piece = os.path.join(work, f'a{index:03d}.m4a')
        if item['voice']:
            run([FFMPEG, '-y', '-loglevel', 'error', '-i', item['voice'],
                 '-af', f"adelay=300|300,apad,atrim=0:{item['seconds']:.3f}",
                 '-c:a', 'aac', '-b:a', '160k', piece])
        else:
            run([FFMPEG, '-y', '-loglevel', 'error', '-f', 'lavfi',
                 '-i', f"anullsrc=r=24000:cl=mono:d={item['seconds']:.3f}",
                 '-c:a', 'aac', '-b:a', '160k', piece])
        pieces.append(piece)
    track = os.path.join(work, 'voice.m4a')
    alist = os.path.join(work, 'audio.txt')
    with open(alist, 'w') as handle:
        for piece in pieces:
            handle.write(f"file '{piece}'\n")
    run([FFMPEG, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', alist,
         '-c', 'copy', track])
    run([FFMPEG, '-y', '-loglevel', 'error', '-i', silent, '-i', track,
         '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
         '-shortest', '-movflags', '+faststart', out_path])
    return {'name': name, 'frames': len(items), 'rendered': len(plan),
            'cues': len(cues), 'voiced': sum(1 for t in timeline if t['voice']), 'out': out_path}


MAX_CLIP_SPEED = 1.8     # 片段最多加速到这个倍数，再快就跟不上了


def _thumb(path):
    """取一张很小的灰度图做帧间比较，够判断动没动，又不至于每帧都解一张 4K。"""
    with Image.open(path) as image:
        return list(image.convert('L').resize((160, 90), Image.BILINEAR).getdata())


def _mad(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def deshimmer(raw_dir):
    """抹掉页面在两个渲染状态之间来回翻造成的抖动。

    录制时助手在流式输出，每个 tick 都让整块面板重新栅格化，文字反锯齿跟着翻，
    源录像里就是严格的 A/B/A/B：相邻帧差 ~2.0，隔一帧差 ~0.03。肉眼看是整栏
    文字持续发抖。

    做法是维持一张「当前在放的参考帧」：来了新帧，如果它和参考帧几乎一样就
    照放；差得明显但又和近期出现过的某个旧状态几乎一样，说明是翻回去了，
    仍然放参考帧；只有真正没见过的新画面才更新参考帧。滚动和点击每帧都是
    新状态，照常放行；静止时画面会彻底定住，不再抖。
    """
    names = sorted(f for f in os.listdir(raw_dir) if f.endswith('.jpg'))
    if len(names) < 3:
        return 0
    ref_name = names[0]
    ref = _thumb(os.path.join(raw_dir, ref_name))
    recent = []              # 近期见过、但不是当前参考帧的状态
    held = 0
    for name in names[1:]:
        cur = _thumb(os.path.join(raw_dir, name))
        d1 = _mad(cur, ref)
        if d1 <= SHIMMER_FLOOR:
            continue                                  # 和参考帧一样，本来就不用动
        if recent and min(_mad(cur, s) for s in recent) < d1 * SHIMMER_RATIO:
            shutil.copyfile(os.path.join(raw_dir, ref_name), os.path.join(raw_dir, name))
            held += 1
            continue                                  # 翻回旧状态了，按住参考帧
        recent.append(ref)
        if len(recent) > STATE_WINDOW:
            recent.pop(0)
        ref, ref_name = cur, name
    return held


def in_window(item, frac):
    """高亮/标注可以带 win: [起, 止]（镜头时长的比例），不带就是全程显示。"""
    win = item.get('win') if isinstance(item, dict) else None
    return True if not win else win[0] <= frac <= win[1]


def clip_from_video(video, start_ms, end_ms, out_dir, spec, fps=FPS, target_s=None):
    """从连续录像里裁一段，逐帧叠标注后重新编码。

    交互镜头（拖节点、拉连线、切视图）必须是连续视频：按帧率抽稀出来的
    是幻灯片，动作看不出是怎么发生的。这里不做去重也不做最短停留，
    原样按录制帧率走，只是把字幕和高亮烧上去。
    """
    os.makedirs(out_dir, exist_ok=True)
    raw = os.path.join(out_dir, 'raw')
    os.makedirs(raw, exist_ok=True)
    for name in os.listdir(raw):
        os.remove(os.path.join(raw, name))
    # 片段常常比配音长，多出来的部分全是静音。先按配音时长适度加速，
    # 加速到上限还装不下的，从尾部裁掉——动作看得清比放完整更重要。
    span_s = (end_ms - start_ms) / 1000.0
    speed = 1.0
    if target_s and span_s > target_s:
        speed = min(MAX_CLIP_SPEED, span_s / target_s)
        if span_s / speed > target_s:
            end_ms = start_ms + int(target_s * speed * 1000)
    vf = f'setpts=PTS/{speed:.4f},fps={fps}' if speed > 1.001 else f'fps={fps}'
    run([FFMPEG, '-y', '-loglevel', 'error', '-ss', f'{start_ms / 1000:.3f}',
         '-to', f'{end_ms / 1000:.3f}', '-i', video,
         '-vf', vf, '-q:v', '3', os.path.join(raw, 'r%05d.jpg')])
    frames = sorted(f for f in os.listdir(raw) if f.endswith('.jpg'))
    if not frames:
        raise SystemExit(f'{video} 的 [{start_ms},{end_ms}] 区间没裁到帧')
    # 片段比配音短时，定格最后一帧补到配音长度。
    # 不补的话音轨会被裁到画面长度，话没说完就切走——这比画面多停一会儿难受得多。
    if target_s:
        need = int(round(target_s * fps))
        if len(frames) < need:
            last = frames[-1]
            for i in range(len(frames), need):
                shutil.copyfile(os.path.join(raw, last),
                                os.path.join(raw, f'r{i + 1:05d}.jpg'))
            frames = sorted(f for f in os.listdir(raw) if f.endswith('.jpg'))
    held = deshimmer(raw)
    if held:
        print(f'  去抖：{os.path.basename(out_dir)} 压掉 {held}/{len(frames)} 帧两态跳变')
    done = os.path.join(out_dir, 'done')
    os.makedirs(done, exist_ok=True)
    for name in os.listdir(done):
        os.remove(os.path.join(done, name))
    # 激光笔沿路径匀速走：pointer_path 是若干个 [x, y] 关键点，
    # 按帧在相邻两点间线性插值，落点跟着讲解走而不是钉在一处。
    path = spec.pop('pointer_path', None)
    for index, name in enumerate(frames):
        shot = dict(spec)
        # 滚动镜头里，高亮框钉在固定坐标上是错的：画面往上走，框还留在原地，
        # 讲到的那句话早就滚出框外了。带 win 的高亮/标注只在镜头的指定时段出现，
        # 于是可以「先流畅滚过去，停稳了再框出来」，两个要求不打架。
        frac = index / max(len(frames) - 1, 1)
        # 过滤之后下标会变，标注的引线是按下标找框的，得跟着重映射；
        # 它挂的那个框这会儿不显示，就干脆不画引线，别指到别的框上。
        kept = [(i, h) for i, h in enumerate(shot.get('highlights', [])) if in_window(h, frac)]
        remap = {old_i: new_i for new_i, (old_i, _) in enumerate(kept)}
        shot['highlights'] = [h for _, h in kept]
        notes = []
        for note in shot.get('notes', []):
            if not in_window(note, frac):
                continue
            target = note.get('attach')
            if isinstance(target, int):
                note = dict(note)
                if target in remap:
                    note['attach'] = remap[target]
                else:
                    note.pop('attach', None)
            notes.append(note)
        shot['notes'] = notes
        if path and len(path) >= 2:
            # 匀速爬过去的光点像卡住了。改成大部分时间停在关键点上，要挪的时候
            # 用一小段时间快速平移过去，两头带缓动，不至于生硬地跳。
            t = index / max(len(frames) - 1, 1) * (len(path) - 1)
            i = min(int(t), len(path) - 2)
            f = t - i
            if f < 1 - POINTER_TRAVEL:
                shot['pointer'] = list(path[i])
            else:
                u = (f - (1 - POINTER_TRAVEL)) / POINTER_TRAVEL
                u = u * u * (3 - 2 * u)
                shot['pointer'] = [path[i][0] + (path[i + 1][0] - path[i][0]) * u,
                                   path[i][1] + (path[i + 1][1] - path[i][1]) * u]
        elif path:
            shot['pointer'] = path[0]
        render(os.path.join(raw, name), os.path.join(done, f'{index:06d}.jpg'), shot)
    return done, len(frames)


def concat(parts, out_path):
    listing = os.path.join(ROOT, 'work', 'parts.txt')
    with open(listing, 'w') as handle:
        for part in parts:
            handle.write(f"file '{part}'\n")
    run([FFMPEG, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', listing,
         '-c', 'copy', '-movflags', '+faststart', out_path])
    return out_path


if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'build':
        batch = os.environ.get('KD_BATCH')
        print(json.dumps(build(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5],
                               int(batch) if batch else None), ensure_ascii=False))
    elif action == 'concat':
        print(concat(sys.argv[2].split(','), sys.argv[3]))
