import c4d


"""
def getSelectedPoints(target):
    bs = target.GetPointS()
    return [i for i in range(target.GetPointCount()) if bs.IsSelected(i)]
"""

def getSelectedPoints(obj):
    bs  = obj.GetPointS()
    sel = bs.GetAll(obj.GetPointCount())
    return [index for index, selected in enumerate(sel) if selected]


def create(pos, name):
    nullObj = c4d.BaseObject(c4d.Onull)
    nullObj.SetName('{}_LOC_{}'.format(name[0], name[1]))
    doc.AddUndo(c4d.UNDOTYPE_NEW, nullObj)
    doc.InsertObject(nullObj)

    nullObj.SetMg(c4d.Matrix(off=pos))
    nullObj[c4d.NULLOBJECT_DISPLAY] = 1
    nullObj[c4d.NULLOBJECT_ORIENTATION] = 1
    doc.SetSelection(nullObj, c4d.SELECTION_ADD)

def selectedPointTo():
    objs = doc.GetSelection()
    if not objs:
        return
    doc.StartUndo()

    for obj in objs:
        doc.SetSelection(obj, c4d.SELECTION_SUB)
        if not isinstance(obj, c4d.PointObject):
            continue

        cache = obj.GetDeformCache() # get deforme cache
        obj = obj if cache is None else cache

        selectedPoints = getSelectedPoints(obj)
        for point in selectedPoints:
            pos = obj.GetPoint(point) * obj.GetMg()
            create(pos, (obj.GetName(), point))

    c4d.CallCommand(12298)
    doc.EndUndo()
    c4d.EventAdd()
if __name__ == '__main__':
    selectedPointTo()
