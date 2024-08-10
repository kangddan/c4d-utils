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
            if obj.GetLayerObject(doc) is not None: # add undo to layerObj
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
            obj.SetLayerObject(layerObj)

def getAllObjs(obj=None, objs=None):
    if objs is None: objs = []
    if obj  is None: obj = doc.GetFirstObject()

    while obj:
        objs.append(obj)
        if obj.GetDown():
            getAllObjs(obj.GetDown(), objs)
        obj = obj.GetNext()
    return objs

def getTags(objs):
    return [tag for obj in objs for tag in obj.GetTags()]

def getNoSoloMaterials(noSoloTags, soloTags):
    allMat    = doc.GetMaterials()
    noSoloMat = set(tag.GetMaterial() for tag in noSoloTags if isinstance(tag, c4d.TextureTag))
    soloMat   = set(tag.GetMaterial() for tag in soloTags   if isinstance(tag, c4d.TextureTag))
    
    # delete duplicate materials
    noSoloMatFinal = noSoloMat - soloMat
    
    # add unused materials
    usedMats = noSoloMat | soloMat
    for _mat in allMat:
        if _mat not in usedMats:
            noSoloMatFinal.add(_mat)
    
    return noSoloMatFinal

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

def updateNoSoloObjsState():
    mainData = doc.GetDataInstance()
    objCount = mainData.GetData(100861122)

    baseIndex = 100861123
    for i in range(objCount):
        subData = mainData.GetData(baseIndex)
        obj     = subData.GetData(0)
        layer   = subData.GetData(1)

        baseIndex += 1
        if layer is None:
            continue
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
        obj.SetLayerObject(layer)

    mainData.SetData(100861121, 1) # end solo

def getNoSoloObjsCurrentState(objs):
    mainData = doc.GetDataInstance()
    if mainData.GetData(100861121) == 0:
        return

    mainData.SetData(100861121, 0)          # set start solo ID
    mainData.SetData(100861122, len(objs))  # set objs count ID

    baseIndex = 100861123
    for i, obj in enumerate(objs):
        # add sub data
        subData = c4d.BaseContainer()
        subData.SetData(0, obj)
        subData.SetData(1, obj.GetLayerObject(doc))
        # ------------------------------------------
        mainData.SetData(baseIndex, subData)
        baseIndex += 1

# ----------------------------------------------------------------

def main():
    doc.StartUndo()
    layer = LayerUtils()

    layerName = '< HIDE_OBJS_LAYER >'
    if layer.exists(layerName):
        layer.delete(layerName)
        updateNoSoloObjsState()
    else:
        sel          = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
        soloLayerObj = layer.createLayer(layerName)
        _soloObjs    = soloObjs(sel)
        noSoloObjs   = removeSelectedObjs(getAllObjs(), _soloObjs)
        
        noSoloTags   = getTags(noSoloObjs)
        noSoloMats   = getNoSoloMaterials(noSoloTags, getTags(_soloObjs))
        
        noSoloObjs.extend(noSoloTags)
        noSoloObjs.extend(noSoloMats)

        getNoSoloObjsCurrentState(noSoloObjs)
        layer.toLayer(noSoloObjs, soloLayerObj)
        
        # Scrolls first active object into visible area
        c4d.CallCommand(100004769)

    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    main()
'''
Revision History
Revision 1: 2024-08-10 : First publish

code by kangddan
https://github.com/kangddan
https://animator.at8.fun/
https://space.bilibili.com/174575687
https://x.com/kangddan1
'''
