from __future__ import print_function


def ForwardUnicastPacket(time_now, destination, nexthop):
    print("FU {0} {1} {2}\n".format(time_now, destination, nexthop), end="")


def DropUnicastPacket(time_now, destAddr):
    print("DUP {0} {1}\n".format(time_now, destAddr), end="")


def DropMulticastPacket(time_now, destAddr, source):
    print("DMP {0} {1} {2}\n".format(time_now, destAddr, source), end="")


def ForwardMulticastPacket(time_now, destAddr, ListOfNextHops):
    ListOfNextHops = sorted(ListOfNextHops)

    for i in ListOfNextHops:
        print("FMP {0} {1} {2}\n".format(time_now, destAddr, i), end="")
