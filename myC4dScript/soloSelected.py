import c4d

LAYERNAME = '< HIDE_OBJS_LAYER >'
ROOT      = doc.GetLayerObjectRoot()

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
    if objs is None: objs = []
    if obj is None: obj = doc.GetFirstObject()

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
    for obj in sel:
        if obj.GetDown() is None:
            continue
        childrens = getAllChildren(obj)
        sel.extend(childrens)
    return removeDuplicates(sel)

def removeSelectedObjs(all_objs, solo_objs):
    solo_guids = {obj.GetGUID() for obj in solo_objs}
    remaining_objs = [obj for obj in all_objs if obj.GetGUID() not in solo_guids]
    return remaining_objs

def objToLayer(objs, layer):
    for obj in objs:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
        obj.SetLayerObject(layer)
# ----------------------------------------------------------------
def setBaseLayer():
    docData  = doc.GetDataInstance()
    objCount = docData.GetData(100861122)
    
    startIndex=100861123
    for obj in range(objCount):
        obj = docData.GetData(startIndex)
        startIndex += 1
        layerObj = docData.GetData(startIndex)
        startIndex += 1
        if layerObj is None:
            continue
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
        obj.SetLayerObject(layerObj)

def setLayerObjsToContainer(objs):
    docData = doc.GetDataInstance()
    docData.SetData(100861122, len(objs)) # set obj count
    startIndex=100861123
    for obj in objs:
        docData.SetData(startIndex, obj)
        startIndex += 1
        layerObj = obj.GetLayerObject(doc)
        docData.SetData(startIndex, layerObj)
        startIndex += 1

def main():
    doc.StartUndo()

    if layerExists(LAYERNAME):
        deleteLayer(LAYERNAME)
        setBaseLayer()
    else:
        solo_layer = createLayer(LAYERNAME)

        all_objs   = getAllObjs()
        solo_objs  = soloObjs()
        updateObjs = removeSelectedObjs(all_objs, solo_objs)
        tags       = getTags(updateObjs)
        updateObjs.extend(tags)

        setLayerObjsToContainer(updateObjs)
        objToLayer(updateObjs, solo_layer)

    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    main()
