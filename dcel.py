"""
Provides DCEL (dict-based), Vertex, hEdge, and Face classes.

Adapted from list-based python2 implementation at: https://github.com/Ylannl/pydcel
"""
import numpy as np
from operator import add, sub
import itertools


class Vertex(object):
    
    def __init__(self, px, py, pz, identifier):
        self.identifier = identifier
        self.x = px
        self.y = py
        self.z = pz
        self.incidentEdge = None
        
    def setTopology(self, newIncedentEdge):
        self.incidentEdge = newIncedentEdge
        
    def p(self, array=False):
        if array:
            return np.array([self.x,self.y,self.z])
        else:
            return (self.x,self.y,self.z)

    def __add__(self, other):
        return tuple([add(pq[0], pq[1]) for pq in zip(self.p(), other.p())])

    def __sub__(self, other):
        return tuple(sub(*pq) for pq in zip(self.p(), other.p()))

    def __repr__(self):
        return "v{} ({}, {}, {})".format(self.identifier, self.x, self.y, self.z)


class hEdge(object):
    
    def __init__(self, identifier):
        self.identifier = identifier
        self.origin = None
        self.twin = None
        self.incidentFace = None
        self.next = None
        self.previous = None

    def setTopology(self, newOrigin, newTwin, newIncindentFace, newNext, newPrevious):
        self.origin = newOrigin
        self.twin = newTwin
        self.incidentFace = newIncindentFace
        self.next = newNext
        self.previous = newPrevious

    def vector(self):
        return self.next.origin - self.origin 
        
    def loop(self):
        """Loop from this hedge to the next ones. Stops when we are at the current one again."""
        yield self
        e = self.next
        while e is not self:
            yield e
            e = e.next
            
    def wind(self):
        """iterate over hedges emerging from vertex at origin in ccw order"""
        yield self
        e = self.previous.twin
        while e is not self:
            yield e
            e = e.previous.twin

    def __repr__(self):
        return "he{}".format(self.identifier)


class Face(object):
    
    def __init__(self, identifier):
        self.identifier = identifier
        self.outerComponent = None
        self.innerComponent = None # do I need this?
        self.normal = None

    def setTopology(self, newOuterComponent, newInnerComponent=None):
        self.outerComponent = newOuterComponent
        self.innerComponent = newInnerComponent
        # calculate and set normal automatically
        e1, e2, e3 = itertools.islice(self.outerComponent.loop(), 3)
        self.normal = np.cross(e2.origin-e1.origin, e3.origin-e2.origin)

        
    def loopOuterVertices(self):
        for e in self.outerComponent.loop():
            yield e.origin

    def __repr__(self):
        # return "face( innerComponent-{}, outerComponent-{} )".format(self.outerComponent, self.innerComponent)
        return "f{}".format(self.identifier)


class DCEL(object):
    
    def __init__(self):
        """Note: safe b/c python3.6 dicts preserve insertion-order of elements"""
        self.vertexDict = {}
        self.hedgeDict = {}
        self.faceDict = {}
        self.infiniteFace = None

    def getNewId(self, D):
        if len(D) == 0:
            return 0
        else:
            return list(D.values())[-1].identifier + 1
        
    def createVertex(self, px, py, pz):
        identifier = self.getNewId(self.vertexDict)
        v = Vertex(px,py,pz, identifier)
        self.vertexDict[identifier] = v
        return v
        
    def createHedge(self):
        identifier = self.getNewId(self.hedgeDict)
        e = hEdge(identifier)
        self.hedgeDict[identifier] = e
        return e
        
    def createFace(self):
        identifier = self.getNewId(self.faceDict)
        f = Face(identifier)
        self.faceDict[identifier] = f
        return f

    def createInfFace(self):
        identifier = "i"
        f = Face(identifier)
        self.infiniteFace = f
        return f

    def insert(self, element):
        """Elements should be created using methods above."""
        if type(element) is Vertex:
            self.vertexDict[element.identifier] = element
        elif type(element) is hEdge:
            self.hedgeDict[element.identifier] = element
        elif type(element) is Face:
            self.faceDict[element.identifier] = element
        else:
            print(type(element), " is an illegal element type.")

    def remove(self, element):
        """Be careful: not a safe removal. References to element may still exist."""
        if type(element) is Vertex:
            del self.vertexDict[element.identifier]
            del element
        elif type(element) is hEdge:
            del self.hedgeDict[element.identifier]
            del element
        elif type(element) is Face:
            del self.faceDict[element.identifier]
            del element
        else:
            print("illegal element type")

    def removeFace(self, face):
        """Remove a face + all of its vertices and halfedges"""
        pass


    def __repr__(self):
        s = "{} \t\t\t{}\n".format("VERTEX", "incidentEdge")
        for v in self.vertexDict.values():
            s += "{}:\t\t{}\n".format(v, v.incidentEdge)

        s += "\n{} \t{}\t{}\t{}\t{}\t{}\n".format("hEDGE","origin","twin","face","next","previous")
        for e in self.hedgeDict.values():
            s += "{}:\t v{}\t{}\t{}\t{}\t{}\n".format(e, e.origin.identifier,
                                  e.twin, e.incidentFace, e.next, e.previous)

        s += "\n{} \t{}\n".format("FACE", "outerComponent")
        for f in self.faceDict.values():
            s += "{}:\t{}\n".format(f, f.outerComponent)
        return s

    def checkEdgeTwins(self):
        for e in self.hedgeDict.values():
            if not e == e.twin.twin:
                print("this edge has a problem with its twin:"),
                print(e)
