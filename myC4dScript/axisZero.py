import c4d

def main():

    sel: list[c4d.BaseObject] = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    if not sel: return
    doc.StartUndo()
    for obj in sel:
        if not isinstance(obj, (c4d.SplineObject, c4d.PolygonObject)):
            continue

        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
        baseMatrix = obj.GetMg()
        points = obj.GetAllPoints()

        obj.SetMg(c4d.Matrix())
        newMatrix = obj.GetMg()
        for child in obj.GetChildren():
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, child)
            child.SetMg(baseMatrix * ~newMatrix * child.GetMg())

        for p in range(len(points)):
            obj.SetPoint(p, baseMatrix * ~newMatrix * points[p])
            
        obj.Message(c4d.MSG_UPDATE)
        c4d.EventAdd()
    doc.EndUndo()

if __name__=='__main__':
    main()