#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import math


def construct_lsalist(linkstate):
    '''construct LSA list'''

    lsalist = {}

    for i in range(len(linkstate)):
        if linkstate[i].get('Opaque-Type') == 4:
            # Get SRGB
            if not linkstate[i].get('Advertising Router') in lsalist:
                lsalist[linkstate[i].get('Advertising Router')] = [0, {}]
            lsalist[linkstate[i].get('Advertising Router')][0] \
                += linkstate[i].get('Segment Routing Range TLV')[1].get('SID Label')

        elif linkstate[i].get('Opaque-Type') == 7:
            # Get Node SID (Index)
            if not linkstate[i].get('Advertising Router') in lsalist:
                lsalist[linkstate[i].get('Advertising Router')] = [0, {}]
            lsalist[linkstate[i].get('Advertising Router')][0] \
                += linkstate[i].get('Prefix SID Sub-TLV')[4].get('Index')

        elif linkstate[i].get('Opaque-Type') == 8:
            # Get Adjacency SID
            if not linkstate[i].get('Advertising Router') in lsalist:
                lsalist[linkstate[i].get('Advertising Router')] = [0, {}]
            if not linkstate[i].get('Extended Link TLV')[2].get('Link ID') in lsalist[linkstate[i].get('Advertising Router')][1]:
                lsalist[linkstate[i].get('Advertising Router')][1][linkstate[i].get(
                    'Extended Link TLV')[2].get('Link ID')] = [0, 0, 0]

            lsalist[linkstate[i].get('Advertising Router')][1][linkstate[i].get('Extended Link TLV')[2].get('Link ID')][0]\
                = linkstate[i].get('Extended Link TLV')[3].get('Link data')

            if linkstate[i].get('Adj-SID Sub-TLV') is not None:
                lsalist[linkstate[i].get('Advertising Router')][1][linkstate[i].get('Extended Link TLV')[2].get('Link ID')][1]\
                    = linkstate[i].get('Adj-SID Sub-TLV')[4].get('Label')
            else:
                lsalist[linkstate[i].get('Advertising Router')][1][linkstate[i].get('Extended Link TLV')[2].get('Link ID')][1]\
                    = linkstate[i].get('LAN-Adj-SID Sub-TLV')[5].get('Label')

    for i in range(len(linkstate)):
        if linkstate[i].get('Opaque-Type') == 1:
            # Get link information(ID, Bandwidth)
            for j in lsalist[linkstate[i].get('Advertising Router')][1].values():
                if linkstate[i].get('Local Interface IP Addresses')[0].get('0') == [j][0][0]:
                    [j][0][2] = linkstate[i].get(
                        'Maximum Reservable Bandwidth')

    return lsalist


def construct_graph(lsalist):
    '''construct graph from linkstate'''

    graph = []
    list_keys = []

    for i in lsalist.keys():
        list_keys.append(i)

    for i in range(len(list_keys)):
        for j in range(i + 1, len(list_keys)):
            for k in lsalist[list_keys[i]][1]:
                if k in lsalist[list_keys[j]][1]:
                    graph.append([list_keys[i], list_keys[j],
                                  lsalist[list_keys[i]][1].get(k)[2]])

    return graph


def with_info_graph(graph, policy):
    for i in range(len(graph)):
        graph[i].insert(2, math.ceil(1000000 / graph[i][2]))
        graph[i].append(policy)

    return graph


def cspf_dijkstra(src, dst,info_graph):
    '''CSPF (constrained dijkstra algorithm)'''
    close_list = dijkstra(src, dst, info_graph)

    constrained_path = info_graph

    return constrained_path


def dijkstra(src, dst, graph):
    '''general dijkstra algorithm'''
    shortest_path = []

    return shortest_path


def path_verification(src, via, info_graph, linkstate):
    '''convert CSPF path to segmentlist'''

    segmentlist = []

    for i in range(len(via)):
        # パスを経由ごとに分解し経路計算を行う
        # 制約付き，制約なしを計算し比較
        constrained_path = cspf_dijkstra(src, via[i], info_graph)
        shortest_path = dijkstra(src, [via][i], info_graph)
        # 制約付き最短経路が最短経路と異なる場合はNode SIDで直接指定不可．迂回路のセグメントリストを構築
        if constrained_path != shortest_path:
            # 宛先一つ前までが最短経路かを調べる，1ずつ減らす
            # 最短が見つかったらそこまでのNode SID 見つからないなら一個前へのAdj SIDをsegmentlistにappend
            # Nodeがさすところをsrcに買えてもう一度検索
            # dstまでが最短経路ならそのNodeを加えて終了
            # src == dstならbreak

        else:
            # 直接Node SIDを指定
            segmentlist.append([linkstate[via[i]][0]])

    # debug
    return segmentlist


# def create_segmentlist(linkstate, src, dst, via):
def create_segmentlist():
    '''create segmentlist'''

    '''debug'''
    with open('dat/ted.json', 'r') as f:
        linkstate = json.load(f)
    src = '192.168.0.1'
    dst = '192.168.0.5'
    via = ['192.168.0.2', '192.168.0.3', '192.168.0.4', '192.168.0.5']
    # BW, avoidnodes
    policy = [0, []]
    '''debug'''

    # Linkstate list from TED
    lsalist = construct_lsalist(linkstate)
    # Make graph for Dijkstra [nodeA, nodeB, cost, ...]
    graph = construct_graph(lsalist)
    # Add information in graph
    info_graph = with_info_graph(graph, policy)
    # Make segmentlist
    segmentlist = path_verification(src, via, info_graph, linkstate)
    print(segmentlist)

#     return segmentlist
    return 0


if __name__ == '__main__':
    create_segmentlist()
