import c4d

def addAttr(source, selectedMorphID, obj):
    linkData = c4d.GetCustomDatatypeDefault(c4d.DTYPE_BASELISTLINK)
    linkData[c4d.DESC_NAME] = 'source'
    linkData[c4d.DESC_HIDE] = True
    linkdataId = obj.AddUserData(linkData)
    obj[linkdataId] = source

    # -------------------------------------------------
    poseMorphSelectedIdData = c4d.GetCustomDatatypeDefault(c4d.DTYPE_REAL)
    poseMorphSelectedIdData[c4d.DESC_NAME] = 'selectedMorphID'
    poseMorphSelectedIdData[c4d.DESC_HIDE] = True
    poseMorphSelectedIdDataId = obj.AddUserData(poseMorphSelectedIdData)
    obj[poseMorphSelectedIdDataId] = selectedMorphID

def copy(obj, morphName):
    correctiveMesh = obj.GetClone()
    doc.AddUndo(c4d.UNDOTYPE_NEW, correctiveMesh)
    correctiveMesh.SetName('{}_{}_copy'.format(obj.GetName(), morphName))
    doc.InsertObject(correctiveMesh)
    correctiveMesh[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 2
    # ------------------------
    for tag in correctiveMesh.GetTags():
        if (tag.CheckType(c4d.Tweights)
         or tag.CheckType(c4d.Tposemorph)):
            tag.Remove()
    for child in correctiveMesh.GetChildren():
        child.Remove()
    return correctiveMesh

def getSelectedMorphInfo(poseMorphTag):
    selectedId = poseMorphTag.GetActiveMorphIndex()
    if selectedId in (-1, 0):
        c4d.gui.MessageDialog('Please select a shape!')
        raise RuntimeError('Please select a shape!')

    shapeName = poseMorphTag.GetMorph(selectedId).GetName()
    return selectedId, shapeName

def main():
    skinMesh = doc.GetActiveObject()
    if skinMesh is None:
        return c4d.gui.MessageDialog('Please select a polygon object!')
    cache = skinMesh.GetDeformCache()
    if cache is None:
        return c4d.gui.MessageDialog('Please select a skin object!')
    poseMorphTag = skinMesh.GetTag(c4d.Tposemorph)
    if poseMorphTag is  None:
        return c4d.gui.MessageDialog('Please add PoseMorph!')

    # --------------------------
    selectedId, shapeName = getSelectedMorphInfo(poseMorphTag)
    # --------------------------
    doc.StartUndo()
    correctiveMesh = copy(skinMesh, shapeName)
    addAttr(skinMesh, selectedId, correctiveMesh)
    correctiveMesh.SetAllPoints([cache.GetMl() * pos for pos in cache.GetAllPoints()])
    correctiveMesh.Message(c4d.MSG_UPDATE)
    # --------------------------

    doc.AddUndo(c4d.UNDOTYPE_CHANGE, skinMesh)
    skinMesh[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
    doc.SetSelection(correctiveMesh, c4d.SELECTION_NEW)
    doc.EndUndo()
    c4d.EventAdd()
if __name__ == '__main__':
    main()
'''
Revision History
Revision 1: 2024-07-25 : First publish

code by kangddan
https://github.com/kangddan
https://animator.at8.fun/
https://space.bilibili.com/174575687
https://x.com/kangddan1
'''