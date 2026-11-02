"""Short memory for sequential views of people and a colourful shared target.

Capture timestamps are kept separately for position and direction. Reading
memory never renews them; stale evidence cannot keep a social region forever.
"""
import itertools
import math

import numpy as np
from social_space_inference import components, convex, directed_attention, pair_relation, viewing_hull


class ColorAttention:
    def __init__(self, person_memory=75.0, object_memory=75.0, nearby_distance=2.5, target_distance=4.5):
        self.person_memory = person_memory
        self.object_memory = object_memory
        self.nearby_distance = nearby_distance
        self.target_distance = target_distance
        self.people, self.objects = {}, {}
        self.next_person = self.next_object = 0
        self.last_object_stamp = -math.inf
        self.invalidated = set()
        self.viewing_evidence = {}
        self.tv_aliases = {}
        self.retired_targets = set()

    def merge_people(self):
        """Retire old stationary fragments without refreshing any capture time."""
        keys = sorted(self.people)
        for index, keep in enumerate(keys):
            if keep not in self.people:
                continue
            a = self.people[keep]
            for drop in keys[index+1:]:
                if drop not in self.people:
                    continue
                b = self.people[drop]
                if np.linalg.norm(a['p']-b['p']) >= .28:
                    continue
                if b['stamp'] > a['stamp']:
                    a['p'], a['stamp'] = b['p'].copy(), b['stamp']
                if b['direction_stamp'] > a['direction_stamp']:
                    for field in ('d', 'direction_stamp', 'direction_since', 'direction_hits'):
                        if field in b:
                            a[field] = b[field]
                aliases = set(a.get('camera_ids', ())) | set(b.get('camera_ids', ()))
                aliases.update(p['camera_id'] for p in (a, b) if 'camera_id' in p)
                a['camera_ids'] = aliases
                self.people.pop(drop)
                self.invalidated.add(drop)

    def prune(self, now):
        self.people = {k: p for k, p in self.people.items()
                       if -0.1 <= now - p['stamp'] < self.person_memory}
        for person in self.people.values():
            if not -0.1 <= now - person['direction_stamp'] < self.person_memory:
                person['d'] = None
        self.objects = {k: p for k, p in self.objects.items() if -0.1 <= now - p['stamp'] < self.object_memory}
        for target in self.objects.values():
            if target.get('geometry_stamp') is not None and now-target['geometry_stamp'] >= self.object_memory:
                target['footprint'] = None
        self.viewing_evidence = {k: v for k, v in self.viewing_evidence.items()
                                 if k[0] in self.people and k[1] in self.objects
                                 and -.1 <= now-v['last'] < 8.}
        self.tv_aliases = {k: v for k, v in self.tv_aliases.items() if v in self.objects}

    def observe_screen_objects(self, objects, stamp):
        """Attach measured screen endpoints to TV tracks without colour cues."""
        used = set()
        for obj in objects:
            p = np.asarray(obj['position'], float)
            boundary = np.asarray(obj['footprint'], float)
            if (p.shape != (3,) or boundary.shape != (2, 2)
                    or not np.isfinite(p).all() or not np.isfinite(boundary).all()
                    or not .2 < np.linalg.norm(boundary[1]-boundary[0]) < 4.
                    or np.max(np.linalg.norm(boundary-p[:2], axis=1)) > 2.):
                continue
            key = self.match_tv(p[:2], boundary)
            if key is None:
                key = ('screen', self.next_object)
                self.next_object += 1
                self.objects[key] = dict(p=p[:2], stamp=stamp, since=stamp, hits=0, source='tv')
            old = self.objects[key]
            if stamp <= old.get('geometry_stamp', -math.inf):
                continue
            old.update(p=boundary.mean(axis=0), footprint=boundary, geometry_stamp=stamp, z=float(p[2]))
            front = np.asarray(obj.get('front', []), float)
            if front.shape == (2,) and np.isfinite(front).all() and np.linalg.norm(front) > .9:
                old['front'] = front/np.linalg.norm(front)
            if stamp > old['stamp'] or old['hits'] == 0:
                old.update(stamp=stamp, hits=old['hits']+1)
            used.add(key)
            self.merge_tv_fragments(key)

    def match_tv(self, point, boundary=None, exclude=()):
        """Associate partial screen centres with their measured surface segment."""
        choices = []
        for key, target in self.objects.items():
            if target['source'] != 'tv' or key in exclude:
                continue
            distance = float(np.linalg.norm(target['p']-point))
            segment = target.get('footprint')
            if segment is None:
                if distance < .55:
                    choices.append((distance, key))
                continue
            a, b = np.asarray(segment)[[0, -1]]
            axis = b-a
            length = float(np.linalg.norm(axis))
            if length < .1:
                continue
            axis /= length
            projection = float((point-a) @ axis)
            normal_distance = abs(float(np.cross(point-a, axis)))
            if not -.2 <= projection <= length+.2 or normal_distance > .2:
                continue
            if boundary is not None:
                direction = boundary[-1]-boundary[0]
                if abs(direction @ axis)/max(np.linalg.norm(direction), 1e-9) < math.cos(math.radians(20)):
                    continue
            choices.append((distance, key))
        return min(choices, default=(math.inf, None), key=lambda item: item[0])[1]

    def merge_tv_fragments(self, keep):
        if self.objects[keep].get('footprint') is None:
            return
        for drop, target in list(self.objects.items()):
            if drop == keep or target['source'] != 'tv':
                continue
            if self.match_tv(target['p'], target.get('footprint'), exclude=(drop,)) != keep:
                continue
            self.objects.pop(drop)
            self.retired_targets.add(drop)
            self.tv_aliases = {a: keep if key == drop else key for a, key in self.tv_aliases.items()}

    def observe_people(self, camera_tracks, orientation_sets, now):
        """Remember camera people, including a peer whose heading is still unknown.

        No LiDAR identity quaternion and no inferred/assumed heading enters here.
        Each direction observation can belong to at most one person per update.
        """
        used_people, used_directions = set(), set()
        fresh_people = [p for p in camera_tracks.values() if -0.1 <= now - p['stamp'] < 1.0]
        # Reserve each head/body measurement for its nearest camera person
        # across all sources. A neighbour must not inherit the same person's
        # body direction after that person's head direction was already used.
        owners = {(source, ident): min(fresh_people, key=lambda p: np.linalg.norm(p['p'] - t['p']), default=None)
                  for source, measurements in enumerate(orientation_sets) for ident, t in measurements.items()}
        for camera_id, observed in camera_tracks.items():
            if not -0.1 <= now - observed['stamp'] < 1.0 or observed['hits'] < 2:
                continue
            choices = [(float(np.linalg.norm(p['p'] - observed['p'])), key) for key, p in self.people.items()
                       if key not in used_people]
            distance, key = min(choices, default=(math.inf, -1))
            if np.linalg.norm(observed['velocity']) >= 0.2:
                # A known camera track may already have walked beyond the
                # spatial association radius. Retire its old viewing corridor.
                departed = [k for k, p in self.people.items() if p.get('camera_id') == camera_id
                            or camera_id in p.get('camera_ids', ())]
                for departed_id in departed:
                    self.people.pop(departed_id)
                    self.invalidated.add(departed_id)
                if distance < 0.8:
                    self.people.pop(key, None)
                    self.invalidated.add(key)
                continue
            if any(np.linalg.norm(self.people[k]['p']-observed['p']) < .28
                   for k in used_people if k in self.people):
                continue
            known = [(d, k) for d, k in choices if d < .75 and
                     (self.people[k].get('camera_id') == camera_id or
                      camera_id in self.people[k].get('camera_ids', ()))]
            if known:
                distance, key = min(known)
            if observed['stamp'] - observed['since'] < 0.2:
                continue
            direction = None
            for source, measurements in enumerate(orientation_sets):
                options = [(float(np.linalg.norm(t['p'] - observed['p'])), ident, t)
                           for ident, t in measurements.items() if (source, ident) not in used_directions
                           and owners[(source, ident)] is observed
                           and -0.1 <= now - t['stamp'] < 2.0 and t['hits'] >= 2 and t['stamp'] - t['since'] >= 0.2]
                error, ident, estimate = min(options, default=(math.inf, -1, None), key=lambda item: item[0])
                if error < 0.65:
                    direction = estimate
                    used_directions.add((source, ident))
                    break
            if distance >= 0.75:
                key = self.next_person
                self.next_person += 1
                self.people[key] = dict(p=observed['p'].copy(), stamp=observed['stamp'],
                                        d=None if direction is None else direction['d'].copy(),
                                        direction_stamp=-math.inf if direction is None else direction['stamp'],
                                        direction_since=-math.inf if direction is None else direction['since'],
                                        direction_hits=0 if direction is None else direction['hits'])
            else:
                old = self.people[key]
                if distance > 0.45:
                    self.invalidated.add(key)
                old['p'], old['stamp'] = observed['p'].copy(), observed['stamp']
                if direction is not None and direction['stamp'] >= old['direction_stamp']:
                    if old['d'] is not None and old['d'] @ direction['d'] < math.cos(math.radians(35)):
                        self.invalidated.add(key)
                    old['d'], old['direction_stamp'] = direction['d'].copy(), direction['stamp']
                    old['direction_since'], old['direction_hits'] = direction['since'], direction['hits']
            used_people.add(key)
            self.people[key]['camera_id'] = camera_id
        self.merge_people()

    def observe_objects(self, objects, stamp):
        if stamp <= self.last_object_stamp:
            return
        self.last_object_stamp = stamp
        used = set()
        for obj in objects:
            p = np.asarray(obj['position'], dtype=float)
            boundary = np.asarray(obj['footprint'], dtype=float)
            if (p.shape != (3,) or boundary.ndim != 2 or boundary.shape[1] != 2
                    or not 2 <= len(boundary) <= 16 or not np.all(np.isfinite(p))
                    or not np.all(np.isfinite(boundary)) or obj['hue_groups'] < 3
                    or np.max(np.linalg.norm(boundary - p[:2], axis=1)) > 3.0):
                continue
            choices = [(float(np.linalg.norm(t['p'] - p[:2])), key) for key, t in self.objects.items()
                       if t['source'] == 'colour' and key not in used and abs(t['z'] - p[2]) < 0.65
                       and 0 <= stamp - t['stamp'] < self.object_memory]
            distance, key = min(choices, default=(math.inf, -1))
            if distance > 0.9:
                key = self.next_object
                self.next_object += 1
                self.objects[key] = dict(p=p[:2].copy(), z=p[2], footprint=boundary, source='colour',
                                         stamp=stamp, since=stamp, hits=1)
            else:
                old = self.objects[key]
                combined = convex([*old['footprint'], *boundary])
                # Preserve the previously seen whole screen if a close view
                # clips it. Bound accumulation to a single modest object.
                if np.linalg.norm(np.ptp(combined, axis=0)) <= 4.0:
                    boundary = combined
                old['footprint'] = boundary
                old['p'] = (boundary.min(axis=0) + boundary.max(axis=0)) / 2
                old['z'], old['stamp'], old['hits'] = p[2], stamp, old['hits'] + 1
            used.add(key)

    def observe_tv_objects(self, tracks, now):
        """A depth-localized YOLO TV is also evidence; keep its timestamps separate.

        A TV label does not refresh colour observations or fabricate screen width.
        """
        for ident, track in tracks.items():
            if not -0.1 <= now - track['stamp'] < 1.5:
                continue
            alias = ('tv', ident)
            key = self.tv_aliases.get(alias)
            if key not in self.objects:
                key = self.match_tv(track['p'])
            if key is None:
                key = alias
            self.tv_aliases[alias] = key
            old = self.objects.get(key)
            if old is None or track['stamp'] > old['stamp']:
                if old is None:
                    old = dict(p=track['p'].copy(), z=0., footprint=None, source='tv',
                               stamp=track['stamp'], since=track['since'], hits=track['hits'])
                    self.objects[key] = old
                else:
                    if old.get('footprint') is None:
                        old['p'] = .65*old['p']+.35*track['p']
                    old.update(stamp=track['stamp'], since=min(old['since'], track['since']),
                               hits=max(old['hits']+1, track['hits']))

    def viewing_angle(self, person, target):
        """Angular miss from a screen segment; head/body direction is not eye gaze."""
        if person.get('d') is None:
            return math.inf
        vector = target['p']-person['p']
        if target.get('front') is not None and (-vector) @ target['front'] <= .1:
            return math.inf
        length = float(np.linalg.norm(vector))
        if not .4 < length <= self.target_distance:
            return math.inf
        direction = person['d']/max(float(np.linalg.norm(person['d'])), 1e-9)
        angle = math.acos(float(np.clip(direction @ (vector/length), -1, 1)))
        footprint = target.get('footprint')
        if footprint is not None:
            rays = np.asarray(footprint)-person['p']
            rays /= np.maximum(np.linalg.norm(rays, axis=1)[:, None], 1e-9)
            # The measured segment subtends an angular interval. A ray inside
            # it has zero miss, including viewers seated off the centre axis.
            bearings = np.arctan2(rays[:, 1], rays[:, 0])
            base = math.atan2(vector[1], vector[0])
            offsets = (bearings-base+math.pi) % (2*math.pi)-math.pi
            heading = (math.atan2(direction[1], direction[0])-base+math.pi) % (2*math.pi)-math.pi
            angle = max(float(offsets.min())-heading, heading-float(offsets.max()), 0.)
        return angle

    def relation(self, a, b):
        return pair_relation(a, b, self.nearby_distance)

    def viewers_face_target(self, members, target):
        if not members or any(p['d'] is None for p in members):
            return False
        return all(self.viewing_angle(p, target) <= math.radians(30) for p in members)

    def facing_target(self, a, b, target):
        return self.viewers_face_target((a, b), target)

    def conversation_groups(self, visible):
        # Confirmed screen attention takes precedence over an incidental
        # one-way person-to-person heading within the broad conversation cone.
        viewers = {ident for (ident, target_id), evidence in self.viewing_evidence.items()
                   if evidence['confirmed'] and ident in self.people and target_id in self.objects
                   and min(self.people[ident]['stamp'], self.people[ident]['direction_stamp'])-evidence['last'] < 8.
                   and self.viewing_angle(self.people[ident], self.objects[target_id]) <= math.radians(40)
                   and visible(self.people[ident]['p'], self.objects[target_id]['p'])}
        edges = [(ia, ib) for (ia, a), (ib, b) in itertools.combinations(self.people.items(), 2)
                 if ia not in viewers and ib not in viewers
                 and self.relation(a, b) == 'conversation' and visible(a['p'], b['p'])]
        return components(edges)

    def parallel_pairs(self, visible):
        # A member of an observed conversation is not simultaneously a viewer
        # in another pair. Resolve conversation components before querying TV.
        chatting = set().union(*self.conversation_groups(visible))
        return [(ia, ib) for (ia, a), (ib, b) in itertools.combinations(self.people.items(), 2)
                if ia not in chatting and ib not in chatting and self.relation(a, b) == 'parallel']

    def viewer_candidates(self, visible):
        """Prefer shared viewing, but one measured heading can locate a TV.

        Conversation members keep their interaction space instead of starting
        an unrelated screen search. Unknown headings never become viewer cues.
        """
        chatting = set().union(*self.conversation_groups(visible))
        people = [(i, p) for i, p in self.people.items() if i not in chatting and p['d'] is not None]
        pairs = [(ia, ib) for (ia, a), (ib, b) in itertools.combinations(people, 2)
                 if self.relation(a, b) == 'parallel']
        return pairs + [(i,) for i, _ in people]

    def contradicted(self, key, visible):
        """Fresh motion/heading evidence removes an old cached region early."""
        if key[0] == 'facing_group':
            members = set(key[1:])
            if members & self.invalidated:
                return True
            if members <= self.people.keys():
                return not any(members <= group for group in self.conversation_groups(visible))
            return False
        members, target_id = set(key[1:-1]), key[-1]
        if target_id in self.retired_targets:
            return True
        if members & self.invalidated:
            return True
        if any(members & group for group in self.conversation_groups(visible)):
            return True
        known = [self.people[i] for i in members if i in self.people and self.people[i]['d'] is not None]
        if target_id in self.objects:
            return any(self.viewing_angle(p, self.objects[target_id]) > math.radians(40) for p in known)
        return False  # Missing data expires by time, not a claim of absence.

    def regions(self, visible, margin, group_margin=0.35, color_enabled=True):
        regions = {}
        for ids in self.conversation_groups(visible):
            members = [self.people[i] for i in sorted(ids)]
            points = [p['p'] for p in members]
            stamps = [p['stamp'] for p in members]
            # Preserve the interaction center when only two of a group's
            # faces are currently measurable; the center may be off the chord.
            for a, b in itertools.combinations(members, 2):
                if self.relation(a, b) != 'conversation' or not visible(a['p'], b['p']):
                    continue
                stamps.extend(person['direction_stamp'] for person, other in ((a, b), (b, a))
                              if directed_attention(person, other))
                center = (a['p'] + b['p']) / 2
                rays = (np.column_stack((a['d'], -b['d']))
                        if a['d'] is not None and b['d'] is not None else None)
                if rays is not None and abs(np.linalg.det(rays)) > math.sin(math.radians(12)):
                    lengths = np.linalg.solve(rays, b['p'] - a['p'])
                    if np.all((lengths > 0) & (lengths < 3.0)):
                        estimate = a['p'] + lengths[0] * a['d']
                        if np.linalg.norm(estimate - center) < 0.85:
                            center = estimate
                points.extend(center + 0.4 * np.array([math.cos(t), math.sin(t)])
                              for t in np.linspace(0, 2 * math.pi, 8, endpoint=False))
            stamp = min(stamps)
            regions[('facing_group', *sorted(ids))] = dict(
                polygon=convex(points), margin=group_margin, stamp=stamp,
                source='nearby people: at least one measured direction towards a peer; TV not required')
        if not color_enabled:
            return regions
        # Each polygon is one viewer-to-screen corridor. The map combines them
        # by union, so unrelated space between viewers is never convex-filled.
        for ident, person in self.people.items():
            if person.get('d') is None:
                continue
            choices = []
            for target_id, target in self.objects.items():
                if (target['hits'] < 2 or target['stamp']-target['since'] < .2
                        or not visible(person['p'], target['p'])):
                    continue
                angle = self.viewing_angle(person, target)
                evidence = self.viewing_evidence.get((ident, target_id))
                threshold = 40 if evidence is not None and evidence.get('confirmed') else 30
                if angle > math.radians(threshold):
                    self.viewing_evidence.pop((ident, target_id), None)
                    continue
                # Prefer actual screen geometry over a nearby duplicate centre
                # observation; otherwise select by alignment before distance.
                duplicate = (target['source'] == 'colour' or target.get('footprint') is None) and any(
                    t['source'] == 'tv' and t.get('footprint') is not None
                    and np.linalg.norm(t['p']-target['p']) < .75
                    for t in self.objects.values())
                if duplicate:
                    continue
                choices.append((angle, np.linalg.norm(target['p']-person['p']), target_id, target))
            if not choices:
                continue
            angle, _, target_id, target = min(choices, key=lambda item: item[:2])
            pair = (ident, target_id)
            # A timer tick or a repeated message cannot count as new evidence.
            stamp = min(person['stamp'], person['direction_stamp'])
            for other in list(self.viewing_evidence):
                if other[0] == ident and other != pair:
                    del self.viewing_evidence[other]
            evidence = self.viewing_evidence.get(pair)
            if evidence is None or stamp-evidence['last'] > 1.5 or ident in self.invalidated:
                evidence = dict(first=stamp, last=stamp, hits=1, confirmed=False)
                self.viewing_evidence[pair] = evidence
            elif stamp > evidence['last']:
                evidence.update(last=stamp, hits=evidence['hits']+1)
            evidence['confirmed'] |= evidence['hits'] >= 3 and stamp-evidence['first'] >= .6
            # A fixed camera cannot always see viewers and the screen together.
            # The orientation tracker already counts distinct capture stamps
            # and resets its stable window on a turn. Preserve that measured
            # history when a screen is discovered later during the same sweep.
            evidence['confirmed'] |= (
                person.get('direction_hits', 0) >= 3
                and person['direction_stamp']-person.get('direction_since', person['direction_stamp']) >= .6)
            if not evidence['confirmed']:
                continue
            is_tv = target['source'] == 'tv'
            footprint = target.get('footprint')
            polygon = viewing_hull(person['p'], person['p'], target['p'], footprint)
            key = ('viewing_tv' if is_tv else 'color_attention', ident, target_id)
            evidence_stamp = min(target['stamp'], stamp)
            regions[key] = dict(
                polygon=polygon, margin=margin, stamp=evidence_stamp,
                attention_score=math.exp(-.5*(angle/math.radians(20))**2),
                source='temporally confirmed viewer + ' + (
                    'RGB-D measured TV segment' if is_tv and footprint is not None else
                    'camera TV; estimated width 1.1m' if is_tv else
                    'RGB-D multicolour target; heuristic'))
        return regions
