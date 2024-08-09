import c4d

def main():
    sel = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)

    doc.StartUndo()
    for obj in sel:
        doc.AddUndo( c4d.UNDOTYPE_CHANGE, obj)
        baseMatrix = obj.GetMg()
        minY = min((baseMatrix * pos).y for pos in obj.GetAllPoints())
        invertMatrix = ~c4d.Matrix(off=c4d.Vector(0, minY, 0))
        obj.SetMg(invertMatrix*baseMatrix)

    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    main()