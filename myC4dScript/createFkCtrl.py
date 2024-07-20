import c4d

def parent(child: c4d.BaseObject, parent: c4d.BaseObject) -> None:
    baseMatrix = child.GetMg()
    child.InsertUnder(parent)
    child.SetMg(baseMatrix)

def moveTo(obj: c4d.BaseObject, target: c4d.BaseObject) -> None:
    obj.SetMg(target.GetMg())

def createFkShape(name: str) -> tuple[c4d.BaseObject, c4d.BaseObject]:
    grp = c4d.BaseObject(c4d.Onull)
    doc.AddUndo(c4d.UNDOTYPE_NEW, grp)
    grp.SetName('{}_{}_{}'.format(name, 'fkCtrl', 'srt'))
    grp[c4d.ID_BASEOBJECT_ROTATION_ORDER] = 5
    grp[c4d.NULLOBJECT_DISPLAY] = 14
    doc.InsertObject(grp)

    ctrl = c4d.BaseObject(5186)
    doc.AddUndo(c4d.UNDOTYPE_NEW, ctrl)
    ctrl.SetName('{}_{}'.format(name, 'fkCtrl'))
    ctrl[c4d.PRIM_RECTANGLE_WIDTH] = 50
    ctrl[c4d.PRIM_RECTANGLE_HEIGHT] = 20
    ctrl[c4d.PRIM_PLANE] = 1
    ctrl[c4d.ID_BASEOBJECT_ROTATION_ORDER] = 5
    ctrl[c4d.ID_BASEOBJECT_USECOLOR] = 2
    ctrl[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(0, 0, 1)
    doc.InsertObject(ctrl)

    parent(ctrl, grp)
    return ctrl, grp

def create(parentCtrl, obj, sel) -> None:
    ctrl, grp = createFkShape(obj.GetName())
    moveTo(grp, obj)

    tag = c4d.BaseTag(1019364)
    doc.AddUndo(c4d.UNDOTYPE_NEW, tag)
    obj.InsertTag(tag)
    tag[c4d.ID_CA_CONSTRAINT_TAG_PSR] = 1
    tag[10006] = 1
    tag[10001] = ctrl

    if parentCtrl:
        parent(grp, parentCtrl)

    child = obj.GetDown()
    while child:
        if child in sel:
            create(ctrl, child, sel)
        child = child.GetNext()

def main() -> None:
    sel: list[c4d.BaseObject] = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    if not sel: return

    doc.StartUndo()
    for obj in sel:
        parent = obj.GetUp()
        if not parent or parent not in sel:
            create(None, obj, sel)
    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    main()