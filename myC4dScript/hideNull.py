import c4d

def getAllObjs(obj=None, objs=None) -> list[c4d.BaseObject]:
    if objs is None: objs = []
    if obj  is None: obj = doc.GetFirstObject()
    
    while obj:
        objs.append(obj)
        if obj.GetDown():
            getAllObjs(obj.GetDown(), objs)
        obj = obj.GetNext()
    return objs

def nullShapeToNone() -> None:
    objs = getAllObjs()

    doc.StartUndo()
    for obj in objs:
        if obj.CheckType(c4d.Onull):
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
            obj[c4d.NULLOBJECT_DISPLAY] = 14

    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    nullShapeToNone()