import c4d

class GetSelectedPointID(object):

    def __init__(self, obj, modeId):
        self.obj    = obj
        self.modeId = modeId

    def run(self) -> list[int]:
        if self.modeId == c4d.Mpoints:
            return self.pointsToId(self.obj)
        elif self.modeId == c4d.Medges:
            return self.edgesToId(self.obj)
        elif self.modeId == c4d.Mpolygons:
            return self.polysToId(self.obj)
        return []

    @staticmethod
    def pointsToId(obj) -> list[int]:
        bs  = obj.GetPointS()
        sel = bs.GetAll(obj.GetPointCount())
        return [index for index, selected in enumerate(sel) if selected]

    @staticmethod
    def polysToId(obj) -> set[int]:
        bs  = obj.GetPolygonS()
        sel = bs.GetAll(obj.GetPolygonCount())
        selPolyId = [index for index, selected in enumerate(sel) if selected]

        # ---------------------------------------------------
        polys: list[c4d.CPolygon] = obj.GetAllPolygons()
        selPointsId = set()
        for index in selPolyId:
            poly:c4d.CPolygon = polys[index]
            selPointsId.update([poly.a, poly.b, poly.c, poly.d])
        return selPointsId

    @staticmethod
    def edgesToId(obj) -> set[int]:
        selEdge: c4d.BaseSelect   = obj.GetEdgeS()
        polys: list[c4d.CPolygon] = obj.GetAllPolygons()

        selectedEdges = set()
        for polyIndex, poly in enumerate(polys):
            edges = [
                (poly.a, poly.b),
                (poly.b, poly.c),
                (poly.c, poly.d if poly.c != poly.d else poly.a),
                (poly.d if poly.c != poly.d else poly.a, poly.a)
            ]
            for edgeIndex, (v1, v2) in enumerate(edges):
                selectionIndex = 4 * polyIndex + edgeIndex
                if selEdge.IsSelected(selectionIndex):
                    selectedEdges.update((v1, v2))

        return selectedEdges

def getSelectedPointsInfo(obj) -> list[int, c4d.Vector]:
    obj      = obj.GetDeformCache() or obj
    pointsID = GetSelectedPointID(obj, doc.GetMode()).run()
    return [[i, obj.GetPoint(i) * obj.GetMg()] for i in pointsID]

def createLoc(pos, name) -> c4d.BaseObject:
    locator = c4d.BaseObject(c4d.Onull)
    locator.SetName('{}_LOC_{}'.format(name[0], name[1]))
    doc.AddUndo(c4d.UNDOTYPE_NEW, locator)
    doc.InsertObject(locator)

    locator.SetMg(c4d.Matrix(off=pos))
    locator[c4d.NULLOBJECT_DISPLAY] = 1
    locator[c4d.NULLOBJECT_ORIENTATION] = 1
    doc.SetSelection(locator, c4d.SELECTION_ADD)

def main():
    sel = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    if not sel or not doc.IsEditMode(): return
    doc.StartUndo()

    for obj in sel:
        doc.AddUndo(c4d.UNDOTYPE_BITS, obj)
        doc.SetSelection(obj, c4d.SELECTION_SUB)
        if not obj.CheckType(c4d.Opoint):
            continue

        pointsInfo = getSelectedPointsInfo(obj)
        for info in pointsInfo:
            createLoc(info[1], (obj.GetName(), info[0]))

    doc.SetMode(c4d.Mmodel)
    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    main()
