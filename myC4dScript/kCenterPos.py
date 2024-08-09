import c4d

def center(vectors):

    minPoint = c4d.Vector(float('inf'), float('inf'), float('inf'))
    maxPoint = c4d.Vector(float('-inf'), float('-inf'), float('-inf'))

    for vector in vectors:
        if vector.x < minPoint.x: minPoint.x = vector.x
        if vector.y < minPoint.y: minPoint.y = vector.y
        if vector.z < minPoint.z: minPoint.z = vector.z

        if vector.x > maxPoint.x: maxPoint.x = vector.x
        if vector.y > maxPoint.y: maxPoint.y = vector.y
        if vector.z > maxPoint.z: maxPoint.z = vector.z

    center = (minPoint + maxPoint) / 2.0
    return center

def main():
    sel = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)

    doc.StartUndo()
    for obj in sel:
        doc.AddUndo( c4d.UNDOTYPE_CHANGE, obj)
        obj           = obj.GetCache() or obj
        baseMatrix    = obj.GetMg()
        basePointsPos = [baseMatrix * pos for pos in obj.GetAllPoints()]
        centerPos     = center(basePointsPos)
        # -------------------------------
        baseMatrix.off = centerPos
        obj.SetMg(baseMatrix)
        obj.SetAllPoints([~baseMatrix * i for i in basePointsPos])
        obj.Message(c4d.MSG_UPDATE)

    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    main()