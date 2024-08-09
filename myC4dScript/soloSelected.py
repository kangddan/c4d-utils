import c4d

class LayerUtils(object):

    def __init__(self):
        self.root = doc.GetLayerObjectRoot()

    def allLayers(self):
        return getAllObjs(self.root.GetDown())

    def exists(self, layerName):
        return layerName in [layer.GetName() for layer in self.allLayers()]

    def layerByName(self, layerName):
        for layer in self.allLayers():
            if layer.GetName() != layerName:
                continue
            return layer
        return None

    def delete(self, layerName):
        if self.exists(layerName):
            layerObj = self.layerByName(layerName)
            doc.AddUndo(c4d.UNDOTYPE_DELETE, layerObj)
            layerObj.Remove()

    def createLayer(self, layerName):
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
        layer.InsertUnder(self.root)
        return layer

    @staticmethod
    def toLayer(objs, layerObj):
        for obj in objs:
            if obj.GetLayerObject(doc) is not None:
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj) # add undo to layerObj
            obj.SetLayerObject(layerObj)

def getAllObjs(obj=None, objs=None):
    objs = objs or []

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

def soloObjs(sel):
    allObjs = sel[:]
    for obj in sel:
        if obj.GetDown() is not None:
            childrens = getAllChildren(obj)
            allObjs.extend(childrens)

    return removeDuplicates(allObjs)

def removeSelectedObjs(all_objs, solo_objs):
    solo_guids = {obj.GetGUID() for obj in solo_objs}
    remaining_objs = [obj for obj in all_objs if obj.GetGUID() not in solo_guids]
    return remaining_objs

# ----------------------------------------------------------------

def setBaseLayer():
    docData = doc.GetDataInstance()
    objCount = docData.GetData(100861122)

    baseIndex = 100861123
    for i in range(objCount):
        objId   = baseIndex + 2 * i
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
        #if layerObj is not None:
        docData.SetData(dataIndex + 1, obj.GetLayerObject(doc))

# ----------------------------------------------------------------

def main():
    doc.StartUndo()
    layer = LayerUtils()

    layerName = '< HIDE_OBJS_LAYER >'
    if layer.exists(layerName):
        layer.delete(layerName)
        setBaseLayer()
    else:
        sel = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
        soloLayerObj = layer.createLayer(layerName)
        noSoloObjs   = removeSelectedObjs(getAllObjs(doc.GetFirstObject()), soloObjs(sel))
        noSoloObjs.extend(getTags(noSoloObjs))
        print(len(noSoloObjs))
        setLayerObjsToContainer(noSoloObjs)
        layer.toLayer(noSoloObjs, soloLayerObj)

        # Scrolls first active object into visible area
        c4d.CallCommand(100004769)

    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    main()
