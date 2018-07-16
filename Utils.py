class lsp_pair(object):
    def __init__(self, h, d):
        self.host = h
        self.distance = d


class event(object):
    def __init__(self):
        self.timestamp = ''
        self.type = ''
        self.unihost = ''
        self.seqno = ''
        self.num_pairs = ''
        self.pairs = ''
        self.multiaddr = ''
        self.TTL = ''
        self.pairs = ''


class node_lsp(object):
    def __init__(self):
        self.source = ''
        self.distances = {}
        self.seqno = ''


class linker(object):
    def __init__(self):
        self.links = {}

    def addLink(self, source, dest, seqno, dist):

        # Create new node link type
        if not self.links.has_key(source):
            self.links[source] = node_lsp()
        else:
            self.links[source].source = source
            self.links[source].seqno = seqno
            self.links[source].distances[dest] = dist

            # Correct links
            if self.links.has_key(dest):
                if self.links[dest].seqno < self.links[source].seqno and self.links[dest].distances.has_key(source):
                    if self.links[source].distances[dest] != self.links[dest].distances[source]:
                        self.links[dest].distances[source] = dist

        return self.links

    def update(self, source):

        if self.links.has_key(source):
            source_dist = self.links[source].distances
            self.links[source].distances = {}

            for i in source_dist:

                if self.links.has_key(i):
                    del self.links[i].distances[source]
        else:
            self.links[source] = node_lsp()

    def allLinks(self):
        return self.links

    def getPrevSeqNo(self, source):
        if self.links.has_key(source):
            return self.links[source].seqno
        else:
            return -1


class multicast(object):
    def __init__(self):
        self.groups = {}

    def group(self, sess_id):

        if self.groups.has_key(sess_id):
            return self.groups[sess_id]['group']
        else:
            return []

    def addSession(self, source, sess_id, ttl):

        if not self.groups.has_key(sess_id):
            dict = {'source': source, 'group': [source], 'ttl': ttl}
            self.groups[sess_id] = dict

    def addGroupMember(self, sess_id, member_id):

        if self.groups.has_key(sess_id):
            group = self.groups[sess_id]['group']

            if member_id not in group:
                group.append(member_id)
                self.groups[sess_id]['group'] = group

    def quitSession(self, sess_id, member_id):

        if self.groups.has_key(sess_id):
            group = self.groups[sess_id]['group']

            if member_id in group:
                group.remove(member_id)
                self.groups[sess_id]['group'] = group
