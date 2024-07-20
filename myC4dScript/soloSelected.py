import c4d
from c4d import gui


class MyUtils(object):
    LAYERNAME = '< HIDE_OBJS_LAYER >'
    ROOT = doc.GetLayerObjectRoot()

    @staticmethod
    def getAllLayers():
        return MyUtils.ROOT.GetChildren()

    @staticmethod
    def layerExists(layers, layerName):
        for layer in layers:
            if layer.GetName() == layerName:
                return True
        return False

    @staticmethod
    def deleteLayer(layers, layerName):
        for layer in layers:
            if layer.GetName() == layerName:
                doc.AddUndo(c4d.UNDOTYPE_DELETE, layer)
                layer.Remove()

    @staticmethod
    def createLayer(layerName):
        layer = c4d.documents.LayerObject()
        doc.AddUndo(c4d.UNDOTYPE_NEW, layer)

        # set layer datas
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
        layer.InsertUnder(MyUtils.ROOT)
        return layer

    @staticmethod
    def getAllObjs(obj=None, objs=None):
        if objs is None: objs = []
        if obj is None: obj = doc.GetFirstObject()

        while obj:
            objs.append(obj)
            if obj.GetDown():
                MyUtils.getAllObjs(obj.GetDown(), objs)
            obj = obj.GetNext()

        return objs

    @staticmethod
    def getTags(objs):
        return [tag for obj in objs for tag in obj.GetTags()]

    @staticmethod
    def getAllChildren(obj, children=None):
        if children is None:
            children = []

        child = obj.GetDown()

        while child:
            children.append(child)
            MyUtils.getAllChildren(child, children)
            child = child.GetNext()
        return children

    @staticmethod
    def removeDuplicates(objects):
        unique = {}
        for obj in objects:
            guid = obj.GetGUID()
            if guid not in unique:
                unique[guid] = obj
        return list(unique.values())

    @staticmethod
    def soloObjs():
        soloList = []
        #selectedObj = doc.GetSelection()
        selectedObj = [obj for obj in doc.GetSelection()
                       if not isinstance(obj, c4d.BaseTag)]

        for obj in selectedObj:
            if obj.GetDown():
                childrens = MyUtils.getAllChildren(obj)
                for children in childrens:
                    soloList.append(children)

        selectedObj.extend(soloList)
        return MyUtils.removeDuplicates(selectedObj)

    @staticmethod
    def removeSelectedObjs(all_objs, solo_objs):
        solo_guids = {obj.GetGUID() for obj in solo_objs}
        remaining_objs = [obj for obj in all_objs if obj.GetGUID() not in solo_guids]
        return remaining_objs

    @staticmethod
    def objToLayer(objs, layer):
        for obj in objs:
            obj.SetLayerObject(layer)
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
###############################################

def getLayerData(objs=None):
    import json

    layerDict = {}
    # create null
    null = c4d.BaseObject(c4d.Onull)
    doc.AddUndo(c4d.UNDOTYPE_NEW, null)
    doc.InsertObject(null)
    null.SetName('{}_LAYER_DATA'.format(MyUtils.LAYERNAME))

    dataMessage = c4d.GetCustomDatatypeDefault(c4d.DTYPE_STRING)
    dataMessage[c4d.DESC_NAME] = "LAYER_DATA"
    null.AddUserData(dataMessage)


    jsonStr = json.dumps(layerDict) # dict to str
    null[c4d.ID_USERDATA, 1] = jsonStr


def main():
    doc.StartUndo()

    if MyUtils.layerExists(MyUtils.getAllLayers(), MyUtils.LAYERNAME):
       MyUtils.deleteLayer(MyUtils.getAllLayers(), MyUtils.LAYERNAME)
    else:
       solo_layer = MyUtils.createLayer(MyUtils.LAYERNAME)

       all_objs = MyUtils.getAllObjs()
       solo_objs = MyUtils.soloObjs()
       newObjs = MyUtils.removeSelectedObjs(all_objs, solo_objs)

       tags = MyUtils.getTags(newObjs)
       newObjs.extend(tags)

       # 获取之前的layer
       #getLayerData()
       ######

       MyUtils.objToLayer(newObjs, solo_layer)

    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    main()
