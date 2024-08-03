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
        
def getPointPos(obj: c4d.BaseObject, index: int) -> c4d.Vector:
    obj = obj.GetDeformCache() or obj # get deforme cache
    return obj.GetPoint(index) * obj.GetMg()

def normalizeWeights(weightData: dict[c4d.BaseObject, float]) -> dict[c4d.BaseObject, float]:
    totalWeight = sum(weightData.values())
    if totalWeight == 1:
        return weightData
    return {joint: weight / totalWeight for joint, weight in weightData.items()}

def getSelectedPointWeight(selectedPoints: list[int],
                           weightTag: c4d.BaseTag) -> dict[int, dict]:
    weightDatas: dict[int, dict] = {}
    for p in selectedPoints:
        data: dict[c4d.BaseObject, float] = {}
        for index in range(weightTag.GetJointCount()):
            pointWeight = weightTag.GetWeight(index, p)
            if pointWeight == 0.0:
                continue
            joint = weightTag.GetJoint(index)
            data[joint] = pointWeight
        weightDatas[p] = normalizeWeights(data)
    return weightDatas

def createLoc(parent, index, vec):
    grp = c4d.BaseObject(c4d.Onull)
    doc.AddUndo(c4d.UNDOTYPE_NEW, grp)
    doc.InsertObject(grp)
    grp[c4d.NULLOBJECT_DISPLAY] = 14
    grp.SetName('{}_weightPin_LOC_{}'.format(parent.GetName(), index))
    grp.InsertUnder(parent)
    matrix = c4d.Matrix()
    matrix.off = vec
    grp.SetMg(matrix)
    return grp


def PinObj(datas: dict[int, dict], obj) -> None:
    for index, data in datas.items():
        vec = getPointPos(obj, index)
        # -----------------------------------
        grp = c4d.BaseObject(c4d.Onull)
        doc.AddUndo(c4d.UNDOTYPE_NEW, grp)
        doc.InsertObject(grp)
        # ------------------------------------------------
        inExcludeData = c4d.InExcludeData()
        userInnExclude = c4d.GetCustomDatatypeDefault(c4d.CUSTOMDATATYPE_INEXCLUDE_LIST)
        userInnExclude[c4d.DESC_NAME] = 'PinLOCS'
        userInnExclude[c4d.DESC_HIDE] = True
        userInnExcludeId = grp.AddUserData(userInnExclude)
        # -----------------------------------------------------
        grp.SetName('weightPin_LOC_' + str(index))
        grp[c4d.NULLOBJECT_DISPLAY] = 1
        # ----------------------------------------
        tag = grp.MakeTag(1019364)
        priorityData = c4d.PriorityData()
        priorityData.SetPriorityValue(c4d.PRIORITYVALUE_MODE, c4d.CYCLE_EXPRESSION)
        priorityData.SetPriorityValue(c4d.PRIORITYVALUE_PRIORITY, 10)
        tag[c4d.EXPRESSION_PRIORITY] = priorityData
        # ----------------------------------------
        tag[c4d.ID_CA_CONSTRAINT_TAG_PSR] = True
        c4d.CallButton(tag, c4d.ID_CA_CONSTRAINT_TAG_PSR_REMOVE)
        startIndex = 10001
        for joint, weight in data.items():
            c4d.CallButton(tag, c4d.ID_CA_CONSTRAINT_TAG_PSR_ADD)
            # ---------------------------------------------------
            loc = createLoc(joint, index, vec)
            tag[startIndex] = loc
            inExcludeData.InsertObject(loc, 1)
            # --------------------------------------------------
            tag[startIndex + 1] = weight
            startIndex += 10
        grp[userInnExcludeId] = inExcludeData
        doc.SetSelection(grp, c4d.SELECTION_ADD)

# ------------------------------------------------------
def isPinLoc(obj):
    if not obj.CheckType(c4d.Onull): return False
    if not obj.GetUserDataContainer(): return False
    if not isinstance(obj[c4d.ID_USERDATA,1], c4d.InExcludeData):return False
    return True

def deleteTargets(obj):
    lst = obj[c4d.ID_USERDATA,1]
    objsCount = lst.GetObjectCount()
    objList = [lst.ObjectFromIndex(doc, i) for i in range(objsCount)]

    for _obj in objList:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, _obj)
        _obj.Remove()

# ------------------------------------------------------
def main() -> None:
    obj = doc.GetActiveObject()
    if obj is None:
        return

    doc.StartUndo()
    if isPinLoc(obj):
        deleteTargets(obj)
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
        obj.Remove()
    else:
        if not isinstance(obj, c4d.PolygonObject):
            c4d.gui.MessageDialog('Please select a polygon object!')
            return

        weightTag = obj.GetTag(c4d.Tweights)
        if weightTag is None:
            c4d.gui.MessageDialog('The selected object has no weight tag!')
            return

        doc.SetSelection(obj, c4d.SELECTION_SUB)
        selPoints  = GetSelectedPointID(obj, doc.GetMode()).run()
        weightData = getSelectedPointWeight(selPoints, weightTag)
        PinObj(weightData, obj)
        c4d.CallCommand(12298)
    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    main()

"""
Revision History
Revision 1: 2024-07-8  : First publish
Revision 2: 2024-07-20 : Add an null obj to the joint
Revision 3: 2024-08-03 : Correctly identify point IDs in point, edge, and polygon modes

code by kangddan
https://github.com/kangddan
https://animator.at8.fun/
https://space.bilibili.com/174575687
https://x.com/kangddan1
"""
