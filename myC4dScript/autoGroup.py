import c4d
from c4d import gui

def createGroup(name: str, suffix: str) -> c4d.BaseObject:
    grp = c4d.BaseObject(c4d.Onull)
    doc.AddUndo(c4d.UNDOTYPE_NEW, grp)
    grp.SetName('{}_{}'.format(name, suffix))
    grp[c4d.NULLOBJECT_DISPLAY] = 14
    return grp

def main(suffix: str) -> None:
    sel: list[c4d.BaseObject] = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    if not sel: return

    doc.StartUndo()
    for obj in sel:
        baseMatrix = obj.GetMg()
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)

        grp = createGroup(obj.GetName(), suffix)
        doc.InsertObject(grp, None, obj, True)
        grp.SetMg(baseMatrix)
        obj.InsertUnder(grp)
        obj.SetMg(baseMatrix)

        doc.SetSelection(grp, c4d.SELECTION_ADD)
        doc.SetSelection(obj, c4d.SELECTION_SUB)
        c4d.CallButton(obj, c4d.ID_BASEOBJECT_FROZEN_RESET)


    doc.EndUndo()
    c4d.EventAdd()

if __name__=='__main__':
    main('srt')