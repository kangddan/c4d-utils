import c4d

def alignObjects():
    sel = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    if not sel or len(sel) < 3: return
    startMg = sel[0].GetMg(); endMg = sel[-1].GetMg()

    # -------------------------------
    baseMatrixs = [obj.GetMg() for obj in sel[1:-1]]
    offset = (endMg.off - startMg.off) / (len(sel)-1)

    # -------------------------------
    newMatrix = []
    newMatrix.append(startMg)
    for index, m in enumerate(baseMatrixs):
        m.off = startMg.off + offset * (index + 1)
    newMatrix.extend(baseMatrixs)
    newMatrix.append(endMg)
    # -------------------------------
    doc.StartUndo()
    for index, obj in enumerate(sel):
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
        obj.SetMg(newMatrix[index])

    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    alignObjects()