import c4d

class ObjectList(object):

    def __init__(self):
        pass

    def run(self, sel=False, typ=None):
        if typ   == 'layer':
            return self.toLayers()
        elif typ == 'tag':
            return self.toTags(sel)
        else:   
            methodMap = {
            'joint' : self.toJoints,
            'camera': self.toCameras,
            'spline': self.toSpline
            }
            objects = self.selected() if sel else self.allObjects()
            return methodMap.get(typ, lambda _objs: _objs)(objects)

    def allObjects(self, obj=None, objs=None):
        if objs is None: objs = []
        if obj  is None:  obj = doc.GetFirstObject()

        while obj:
            objs.append(obj)
            if obj.GetDown():
                self.allObjects(obj.GetDown(), objs)
            obj = obj.GetNext()
        return objs

    def toLayers(self):
        return self.allObjects(doc.GetLayerObjectRoot().GetDown())

    def toTags(self, sel=False):
        objects = self.selected() if sel else self.allObjects()
        tags = []
        for obj in objects:
            if isinstance(obj, c4d.BaseTag):
                tags.append(obj)
            else:
                for tag in obj.GetTags():
                    tags.append(tag)  
        return tags
    
    def _filterObjsByType(self, typ, objects):
        return [obj for obj in objects if obj.CheckType(typ)]

    def toJoints(self, objects):
        return self._filterObjsByType(c4d.Ojoint, objects)

    def toCameras(self, objects):
        return self._filterObjsByType(c4d.Ocamera, objects)

    def toSpline(self, objects):
        return self._filterObjsByType(c4d.Ospline, objects)

    def selected(self):
        return doc.GetSelection()

def ls(sel=False, typ=None):
    _ls = ObjectList()
    return _ls.run(sel=sel, typ=typ)


sel = ls(sel=True, typ='tag')
print(sel)