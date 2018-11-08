"""Module for graph traversal methods."""
from __future__ import absolute_import

from ._ffi.function import _init_api
from . import backend as F
from . import utils

__all__ = ['bfs_nodes_generator', 'topological_nodes_generator',
           'dfs_edges_generator', 'dfs_labeled_edges_generator',]

def bfs_nodes_generator(graph, source, reversed=False):
    """Node frontiers generator using breadth-first search.

    Parameters
    ----------
    graph : DGLGraph
        The graph object.
    source : list, tensor of nodes
        Source nodes.
    reversed : bool, optional
        If true, traverse following the in-edge direction.

    Returns
    -------
    list of node frontiers
        Each node frontier is a list, tensor of nodes.
    """
    ghandle = graph._graph._handle
    source = utils.toindex(source).todgltensor()
    ret = _CAPI_DGLBFSNodes(ghandle, source, reversed)
    all_nodes = utils.toindex(ret(0)).tousertensor()
    # TODO(minjie): how to support directly creating python list
    sections = utils.toindex(ret(1)).tousertensor().tolist()
    return F.split(all_nodes, sections, dim=0)

def topological_nodes_generator(graph, reversed=False):
    """Node frontiers generator using topological traversal.

    Parameters
    ----------
    graph : DGLGraph
        The graph object.
    reversed : bool, optional
        If true, traverse following the in-edge direction.

    Returns
    -------
    list of node frontiers
        Each node frontier is a list, tensor of nodes.
    """
    ghandle = graph._graph._handle
    ret = _CAPI_DGLTopologicalNodes(ghandle, reversed)
    all_nodes = utils.toindex(ret(0)).tousertensor()
    # TODO(minjie): how to support directly creating python list
    sections = utils.toindex(ret(1)).tousertensor().tolist()
    return F.split(all_nodes, sections, dim=0)

def dfs_edges_generator(graph, source, reversed=False):
    """Edge frontiers generator using depth-first-search (DFS).

    Multiple source nodes can be specified to start the DFS traversal. One
    needs to make sure that each source node belongs to different connected
    component, so the frontiers can be easily merged. Otherwise, the behavior
    is undefined.

    Parameters
    ----------
    graph : DGLGraph
        The graph object.
    source : list, tensor of nodes
        Source nodes.
    reversed : bool, optional
        If true, traverse following the in-edge direction.

    Returns
    -------
    list of edge frontiers
        Each edge frontier is a list, tensor of edges.
    """
    ghandle = graph._graph._handle
    source = utils.toindex(source).todgltensor()
    ret = _CAPI_DGLDFSEdges(ghandle, source, reversed)
    all_edges = utils.toindex(ret(0)).tousertensor()
    # TODO(minjie): how to support directly creating python list
    sections = utils.toindex(ret(1)).tousertensor().tolist()
    return F.split(all_edges, sections, dim=0)

def dfs_labeled_edges_generator(
        graph,
        source,
        reversed=False,
        has_reverse_edge=False,
        has_nontree_edge=False,
        return_labels=True):
    """Produce edges in a depth-first-search (DFS) labeled by type.

    There are three labels: FORWARD(0), REVERSE(1), NONTREE(2)

    A FORWARD edge is one in which `u` has been visisted but `v` has not. A
    REVERSE edge is one in which both `u` and `v` have been visisted and the
    edge is in the DFS tree. A NONTREE edge is one in which both `u` and `v`
    have been visisted but the edge is NOT in the DFS tree.

    Multiple source nodes can be specified to start the DFS traversal. One
    needs to make sure that each source node belongs to different connected
    component, so the frontiers can be easily merged. Otherwise, the behavior
    is undefined.

    Parameters
    ----------
    graph : DGLGraph
        The graph object.
    source : list, tensor of nodes
        Source nodes.
    reversed : bool, optional
        If true, traverse following the in-edge direction.
    has_reverse_edge : bool, optional
        True to include reverse edges.
    has_nontree_edge : bool, optional
        True to include nontree edges.
    return_labels : bool, optional
        True to return the labels of each edge.

    Returns
    -------
    list of edge frontiers
        Each edge frontier is a list, tensor of edges.
    list of list of int
        Label of each edge, organized in the same as the edge frontiers.
    """
    ghandle = graph._graph._handle
    source = utils.toindex(source).todgltensor()
    ret = _CAPI_DGLDFSLabeledEdges(
            ghandle,
            source,
            reversed,
            has_reverse_edge,
            has_nontree_edge,
            return_labels)
    all_edges = utils.toindex(ret(0)).tousertensor()
    # TODO(minjie): how to support directly creating python list
    if return_labels:
        all_labels = utils.toindex(ret(1)).tousertensor()
        sections = utils.toindex(ret(2)).tousertensor().tolist()
        return (F.split(all_edges, sections, dim=0),
                F.split(all_labels, sections, dim=0))
    else:
        sections = utils.toindex(ret(1)).tousertensor().tolist()
        return F.split(all_edges, sections, dim=0)

_init_api("dgl.traversal")