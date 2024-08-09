import c4d

ROOT = doc.GetLayerObjectRoot()
def getAllLayers():
    return ROOT.GetChildren()

def layerExists(layerName):
    for layer in getAllLayers():
        if layer.GetName() == layerName:
            return True
    return False

def deleteLayer(layerName):
    for layer in getAllLayers():
        if layer.GetName() != layerName:
            continue
        doc.AddUndo(c4d.UNDOTYPE_DELETE, layer)
        layer.Remove()

def createLayer(layerName):
    layer = c4d.documents.LayerObject()
    doc.AddUndo(c4d.UNDOTYPE_NEW, layer)
    layer.SetLayerData(doc, data={'solo':False,
                                  'view':False,
                                  'render':False,
                                  'manager':False,
                                  'locked':False,
                                  'generators':False,
                                  'expressions':False,
                                  'color':c4d.Vector(0, 0, 0),
                                  'deformers':False,
                                  'animation':False,
                                  'xref':True})
    layer.SetName(layerName)
    layer.InsertUnder(ROOT)
    return layer

def getAllObjs(obj=None, objs=None):
    objs = objs or []
    obj  = obj  or doc.GetFirstObject()

    while obj:
        objs.append(obj)
        if obj.GetDown():
            getAllObjs(obj.GetDown(), objs)
        obj = obj.GetNext()
    return objs

def getTags(objs):
    return [tag for obj in objs for tag in obj.GetTags()]

def getAllChildren(obj, children=None):
    if children is None:
        children = []
    child = obj.GetDown()
    while child:
        children.append(child)
        getAllChildren(child, children)
        child = child.GetNext()
    return children

def removeDuplicates(objects):
    unique = {}
    for obj in objects:
        guid = obj.GetGUID()
        if guid not in unique:
            unique[guid] = obj
    return list(unique.values())

def soloObjs():
    sel = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    allObjs = sel[:]
    for obj in sel:
        #  Scrolls first active object into visible area
        c4d.CallCommand(100004769)
        if obj.GetDown() is not None:
            childrens = getAllChildren(obj)
            allObjs.extend(childrens)

    return removeDuplicates(allObjs)

def removeSelectedObjs(all_objs, solo_objs):
    solo_guids = {obj.GetGUID() for obj in solo_objs}
    remaining_objs = [obj for obj in all_objs if obj.GetGUID() not in solo_guids]
    return remaining_objs

def objToLayer(objs, layer):
    for obj in objs:

        if obj.GetLayerObject(doc) is not None:
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj) # add undo to layerObj
        obj.SetLayerObject(layer)

# ----------------------------------------------------------------

def setBaseLayer():
    docData = doc.GetDataInstance()
    objCount = docData.GetData(100861122)

    baseIndex = 100861123
    for i in range(objCount):
        objId = baseIndex + 2 * i
        layerId = baseIndex + 2 * i + 1

        obj      = docData.GetData(objId)
        layerObj = docData.GetData(layerId)

        if layerObj is None:
            continue
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
        obj.SetLayerObject(layerObj)

def setLayerObjsToContainer(objs):
    docData = doc.GetDataInstance()
    docData.SetData(100861122, len(objs))  # Set objs count

    baseIndex = 100861123
    for i, obj in enumerate(objs):
        dataIndex = baseIndex + 2 * i
        docData.SetData(dataIndex, obj)

        layerObj = obj.GetLayerObject(doc)
        if layerObj is not None:
            docData.SetData(dataIndex + 1, obj.GetLayerObject(doc))

# ----------------------------------------------------------------
LAYERNAME = '< HIDE_OBJS_LAYER >'
def main():
    doc.StartUndo()

    if layerExists(LAYERNAME):
        deleteLayer(LAYERNAME)
        setBaseLayer()
    else:
        solo_layer = createLayer(LAYERNAME)
        noSoloObjs = removeSelectedObjs(getAllObjs(), soloObjs())
        noSoloObjs.extend(getTags(noSoloObjs))

        setLayerObjsToContainer(noSoloObjs)
        objToLayer(noSoloObjs, solo_layer)

    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    main()
