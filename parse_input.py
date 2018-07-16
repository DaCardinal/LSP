from __future__ import print_function

import re
import sys

import Utils
import EWG
import DUSP
import produce_output as scan

# Event types
EVENT_INIT = 0
EVENT_LSP = 1
EVENT_UFWD = 2
EVENT_MFWD = 3
EVENT_ADV = 4
EVENT_JOIN = 5
EVENT_QUIT = 6

EINIT = re.compile(r'^(\d+\s+)I(\s+\d+\s+)')
EMFWD = re.compile(r'^(\d+\s+)F(\s+\d+\s+\d+\s+)')
EUFWD = re.compile(r'^(\d+\s+)F(\s+\d+)')
EJOIN = re.compile(r'^(\d+\s+)J(\s+\d+\s+\d+\s+)')
EQUIT = re.compile(r'^(\d+\s+)Q(\s+\d+\s+\d+\s+)')
EADV = re.compile(r'^(\d+\s+)A(\s+\d+\s+\d+\s+\d+\s+)')
ELSP = re.compile(r'^(\d+\s+)L(\s+\d+\s+\d+\s+)(.*)')
PAIRS = re.compile(r'^<(\d+),(\s+\d+)(.*)')
global_source = ''


def parse_event(line, evt):
    # Skip blank lines and comments and blank lines
    if not line.startswith("#") and line not in ['\n', '\r\n', '\r', '\0']:
        # print(line, end="")

        if EMFWD.match(line):
            # Multicast forwarding event
            attrs = EMFWD.match(line).group(0).split()
            evt.timestamp = attrs[0]
            evt.unihost = attrs[2]
            evt.multiaddr = attrs[3]
            evt.type = EVENT_MFWD

            return evt
        elif EUFWD.match(line):
            # Unicast forwarding event
            attrs = EUFWD.match(line).group(0).split()
            evt.timestamp = attrs[0]
            evt.unihost = attrs[2]
            evt.type = EVENT_UFWD

            return evt
        elif EJOIN.match(line):
            # Multicast join evet
            attrs = EJOIN.match(line).group(0).split()
            evt.timestamp = attrs[0]
            evt.unihost = attrs[2]
            evt.multiaddr = attrs[3]
            evt.type = EVENT_JOIN

            return evt
        elif EQUIT.match(line):
            # Multicast quit evet
            attrs = EQUIT.match(line).group(0).split()
            evt.timestamp = attrs[0]
            evt.unihost = attrs[2]
            evt.multiaddr = attrs[3]
            evt.type = EVENT_QUIT

            return evt
        elif EADV.match(line):
            # Multicast advertisement evet
            attrs = EADV.match(line).group(0).split()
            evt.timestamp = attrs[0]
            evt.unihost = attrs[2]
            evt.multiaddr = attrs[3]
            evt.TTL = attrs[4]
            evt.type = EVENT_ADV

            return evt
        else:
            # Initialization, link-state packet, or garbage

            if EINIT.match(line):
                attrs = EINIT.match(line).group(0).split()
                evt.timestamp = attrs[0]
                evt.unihost = attrs[2]
                global global_source
                global_source = int(attrs[2])
                evt.seqno = 0

                evt.type = EVENT_INIT
            elif ELSP.match(line):
                attrs = ELSP.match(line).group(0).split()
                evt.timestamp = attrs[0]
                evt.unihost = attrs[2]
                evt.seqno = attrs[3]

                evt.type = EVENT_LSP
            else:
                return -1

            # Now, munge through the lsp-pairs
            # This is somewhat painful, so don't look
            attrs_p = re.findall(r'<([^>]+)>', line)

            # Count the left braces, so we know how much space to allocate
            pair_list = []

            for i in attrs_p:
                (p_host, p_distance) = i.split(',')
                new_pair = Utils.lsp_pair(int(p_host), int(p_distance))
                pair_list.append(new_pair)

            evt.num_pairs = len(attrs_p)
            evt.pairs = pair_list

            return evt

    return -1


def dump(evt):
    t = -1 if evt == -1 else evt.type

    if t == EVENT_JOIN:
        print("JOIN, id = {0}, addr = {1}\n".format(evt.unihost, evt.multiaddr))
    elif t == EVENT_QUIT:
        print("QUIT, id = {0}, addr = {1}\n".format(evt.unihost, evt.multiaddr))
    elif t == EVENT_ADV:
        print("ADV, id = {0}, addr = {1}, TTL = {2}\n".format(evt.unihost,
                                                              evt.multiaddr, evt.TTL))
    elif t == EVENT_UFWD:
        print("UFWD, host = {0}\n".format(evt.unihost))
    elif t == EVENT_MFWD:
        print("MFWD, source = {0}, addr = {1}\n".format(evt.unihost, evt.multiaddr))
    elif t == EVENT_LSP or t == EVENT_INIT:
        if t == EVENT_INIT:
            print("INIT, id = {0}, ".format(evt.unihost))
        else:
            print("LSP, source = {0}, seqno = {1}, ".format(evt.unihost, evt.seqno))

        print("PAIRS = ")

        for i in range(evt.num_pairs):
            print("<{0}, {1}> ".format(evt.pairs[i].host, evt.pairs[i].distance))

        print("\n");
    else:
        print("ERROR: Invalid event parsed. \n");


def interceptor(evt, ST, links, multicast):
    t = -1 if evt == -1 else evt.type

    if t == EVENT_LSP or t == EVENT_INIT:
        if t == EVENT_INIT:
            ST[int(evt.unihost)] = 0
            source = 0
        else:
            if not int(evt.unihost) in ST.keys():
                ST[int(evt.unihost)] = len(ST)
                source = int(ST[int(evt.unihost)])
            else:
                source = int(ST.get(int(evt.unihost)))

        seqno = int(evt.seqno)

        if seqno > links.getPrevSeqNo(source):

            links.update(source)
            for i in range(evt.num_pairs):
                node = int(evt.pairs[i].host)

                if node not in ST:
                    ST[node] = len(ST)

                links.addLink(source, int(ST[node]), int(evt.seqno), int(evt.pairs[i].distance))

    elif t == EVENT_UFWD:
        global global_source
        INV_ST = {v: k for k, v in ST.iteritems()}
        source = ST[global_source]
        destination = ST[int(evt.unihost)]
        _links = links.allLinks()

        # Build EWG
        e = EWG.EdgeWeightedGraph(len(ST))
        for i in _links:
            link_dist = _links[i].distances
            link_source = _links[i].source

            for j in link_dist:
                e.EdgeWeightedGraph(link_source, j, link_dist[j])

        # Run Dijkstra
        d = DUSP.DijkstraUndirected(e, source)

        pathway = d.pathTo(ST[int(evt.unihost)])

        if pathway:
            if len(pathway) > 1:
                scan.ForwardUnicastPacket(evt.timestamp, INV_ST[destination], INV_ST[pathway[1]])
        else:
            scan.DropUnicastPacket(evt.timestamp, INV_ST[destination])
    elif t == EVENT_ADV:
        multicast.addSession(ST[int(evt.unihost)], int(evt.multiaddr), int(evt.TTL))
    elif t == EVENT_JOIN:
        multicast.addGroupMember(int(evt.multiaddr), ST[int(evt.unihost)])
    elif t == EVENT_QUIT:
        multicast.quitSession(int(evt.multiaddr), ST[int(evt.unihost)])
    elif t == EVENT_MFWD:
        node_source = ST[int(evt.unihost)]
        sess_id = int(evt.multiaddr)
        INV_ST = {v: k for k, v in ST.iteritems()}

        # Remove node source from multicast group
        multicast_group = multicast.group(sess_id)

        # Build EWG
        _links = links.allLinks()

        # Build EWG
        e = EWG.EdgeWeightedGraph(len(ST))
        for i in _links:
            link_dist = _links[i].distances
            link_source = _links[i].source

            for j in link_dist:
                e.EdgeWeightedGraph(link_source, j, link_dist[j])

        # Run Dijkstra
        d = DUSP.DijkstraUndirected(e, node_source)
        hops = {}
        counter = 0
        error_flag = True

        # Check if multicast group exists
        if not multicast_group:
            scan.DropMulticastPacket(evt.timestamp, sess_id, INV_ST[node_source])
        else:
            for m in multicast_group:
                pathway = d.pathTo(m)
                counter += 1

                if 0 in pathway and m != node_source:
                    error_flag = False

                    # Calculate next hop
                    if len(pathway) == 1:
                        next_hop = pathway[0]
                        hops[INV_ST[next_hop]] = 1
                    else:

                        for p in range(len(pathway)):
                            if pathway[p] == 0:
                                next_hop = pathway[p + 1]
                                hops[INV_ST[next_hop]] = 1

                if counter == len(multicast_group):
                    scan.ForwardMulticastPacket(evt.timestamp, sess_id, hops.keys())

                if error_flag and counter == len(multicast_group):
                    scan.DropMulticastPacket(evt.timestamp, sess_id, INV_ST[node_source])

    return ST, links, multicast


def anydup(haystack, needle):
    new_list = [x for x in haystack if haystack.count(x) > 1]

    return needle in new_list


def main():
    evt = Utils.event
    filename = str(sys.argv[1])
    f = open(filename, "r")
    ST = {}
    links = Utils.linker()
    multicast = Utils.multicast()

    try:
        line = f.readline()

        while line:
            wow = parse_event(line, evt)

            if wow != -1:
                (ST, links, multicast) = interceptor(evt, ST, links, multicast)
            line = f.readline()

    except IOError:
        print("Could not open file!")


main()
