import c4d

def psr(obj):
    obj.SetRelPos(c4d.Vector(0,0,0))
    obj.SetRelScale(c4d.Vector(1,1,1))
    obj.SetRelRot(c4d.Vector(0,0,0))

def resetUserData(obj):
    userData = obj.GetUserDataContainer()
    if not userData: return

    for descId, container in userData:
        if container.GetInt32(c4d.DESC_CUSTOMGUI) == 1: # grp
            continue
        
        defaultValue = container[c4d.DESC_DEFAULT]
        attrName = container[c4d.DESC_NAME]
        if defaultValue is None:
            print('The property does not have a default valuet -> {}'.format(attrName))
            continue
        try: obj[descId] = defaultValue
        except:
            print('The property does not have a default valuet -> {}'.format(attrName))

def main():
    baseObjs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    if not baseObjs: return

    doc.StartUndo()
    for obj in baseObjs:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
        psr(obj); resetUserData(obj)
    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    main()