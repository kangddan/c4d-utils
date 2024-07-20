import c4d

def getPointPos(obj: c4d.BaseObject, index: int) -> c4d.Vector:
    cache = obj.GetDeformCache() # get deforme cache
    obj = obj if cache is None else cache
    return obj.GetPoint(index) * obj.GetMg()

def normalizeWeights(weightData: dict[c4d.BaseObject, float]) -> dict[c4d.BaseObject, float]:
    totalWeight = sum(weightData.values())
    if totalWeight == 1:
        return weightData
    return {joint: weight / totalWeight for joint, weight in weightData.items()}

def getSelectedPoints(obj: c4d.BaseObject) -> list[int]:
    bs  = obj.GetPointS()
    sel = bs.GetAll(obj.GetPointCount())
    return [index for index, selected in enumerate(sel) if selected]

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

def createLoc(parent, vec):
    grp = c4d.BaseObject(c4d.Onull)
    doc.AddUndo(c4d.UNDOTYPE_NEW, grp)
    doc.InsertObject(grp)
    grp[c4d.NULLOBJECT_DISPLAY] = 14
    grp.SetName('{}_weightPin_LOC'.format(parent.GetName()))
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
            loc = createLoc(joint, vec)
            tag[startIndex] = loc

            # --------------------------------------------------
            tag[startIndex + 1] = weight
            startIndex += 10

        doc.SetSelection(grp, c4d.SELECTION_ADD)

def main() -> None:
    obj = doc.GetActiveObject()
    if not isinstance(obj, c4d.PolygonObject):
        c4d.gui.MessageDialog('Please select a polygon object!')
        return
    
    weightTag = obj.GetTag(c4d.Tweights)
    if weightTag is None:
        c4d.gui.MessageDialog('The selected object has no weight tag!')
        return
        
    doc.StartUndo()
    doc.SetSelection(obj, c4d.SELECTION_SUB)
    selPoints  = getSelectedPoints(obj)
    weightData = getSelectedPointWeight(selPoints, weightTag)
    PinObj(weightData, obj)
    c4d.CallCommand(12298)
    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    main()