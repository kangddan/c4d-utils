import c4d

def moveToSelected():
    objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)
    if len(objs) < 2:
        return

    doc.StartUndo()
    matrix = objs[-1].GetMg()
    for obj in objs[:-1]:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
        obj.SetMg(matrix)
    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    moveToSelected()