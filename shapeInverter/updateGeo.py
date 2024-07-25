import c4d

def getBasePointsPos(matrix, poseMorphTag):
    baseNode    = poseMorphTag.GetMorphBase().GetFirst()
    poiontCount = baseNode.GetPointCount()
    return [matrix * baseNode.GetPoint(i) for i in range(poiontCount)]

def setMorphPoints(matrix, shapeId, poseMorphTag, pointsPos):
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, poseMorphTag)
    selMorph = poseMorphTag.GetMorph(shapeId)
    selMorph.SetMode(doc, poseMorphTag,
            c4d.CAMORPH_MODE_FLAGS_ALL | c4d.CAMORPH_MODE_FLAGS_EXPAND,
            c4d.CAMORPH_MODE_REL)

    selMorphNode = selMorph.GetFirst()
    for index, pos in enumerate(pointsPos):
        selMorphNode.SetPoint(index, matrix * pos)

def updatePos(list1, list2):
    return [p1 - p2 for p1, p2 in zip(list1, list2)]

# --------------------------------------------------------------------------
def getSelectedShapeRelPointsPos(shapeId, poseMorphTag):
    selMorph = poseMorphTag.GetMorph(shapeId)
    selMorph.SetMode(doc, poseMorphTag,
            c4d.CAMORPH_MODE_FLAGS_ALL | c4d.CAMORPH_MODE_FLAGS_EXPAND,
            c4d.CAMORPH_MODE_REL)
    selMorphNode = selMorph.GetFirst()
    PointCount   = selMorphNode.GetPointCount()
    if PointCount == 0:
        basePointCount = poseMorphTag.GetMorphBase().GetFirst().GetPointCount()
        return [c4d.Vector(0, 0, 0) for i in range(basePointCount)]
    else:
        return [selMorphNode.GetPoint(i) for i in range(PointCount)]

def isCorrectiveMesh(obj):
    if obj is None:
        return False
    userData = obj.GetUserDataContainer()
    if not userData:
        return False
    if userData[0][1][c4d.DESC_NAME] != 'source':
        return False
    return True

# --------------------------------------------------------------------------
def main():
    correctiveMesh = doc.GetActiveObject()
    if not isCorrectiveMesh(correctiveMesh):
        return c4d.gui.MessageDialog('Please select a corrective Mesh!')

    doc.StartUndo()
    doc.AddUndo(c4d.UNDOTYPE_DELETE, correctiveMesh)
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, correctiveMesh)
    # -----------------------------------------------------------------------

    localMatrix       = correctiveMesh.GetMl()
    skinMesh          = correctiveMesh[c4d.ID_USERDATA, 1]
    selectedMorphId   = int(correctiveMesh[c4d.ID_USERDATA, 2])
    weightTag         = skinMesh.GetTag(c4d.Tweights)
    poseMorphTag      = skinMesh.GetTag(c4d.Tposemorph)

    basePointsPos       = getBasePointsPos(localMatrix, poseMorphTag)
    correctivePointsPos = [localMatrix * pos for pos in correctiveMesh.GetAllPoints()]
    skinMeshPointsPos   = [localMatrix * pos for pos in skinMesh.GetAllPoints()]

    # ------------------------------------------------------
    jointCount = weightTag.GetJointCount()
    pointCount = correctiveMesh.GetPointCount()

    invertBindMatrices = [weightTag.GetJointRestState(jointIndex)['m_oMi'] for jointIndex in range(jointCount)]
    jointMatrices      = [weightTag.GetJoint(jointIndex).GetMg() for jointIndex in range(jointCount)]
    weights            = [[weightTag.GetWeight(jointIndex, pointIndex) for pointIndex in range(pointCount)] for jointIndex in range(jointCount)]

    for pointIndex in range(pointCount):
        baseMatrix = 0 * c4d.Matrix()

        for jointIndex in range(jointCount):
            weight = weights[jointIndex][pointIndex]
            if weight > 0:
                baseMatrix += weight * (jointMatrices[jointIndex] * invertBindMatrices[jointIndex])

        correctivePointsPos[pointIndex] = ~baseMatrix * correctivePointsPos[pointIndex]

    newCorrectivePointsPos = [~localMatrix * pos for pos in correctivePointsPos]
    # --------------------------------------------------------------------------
    selShapePointsPos = getSelectedShapeRelPointsPos(selectedMorphId, poseMorphTag)
    offsetPoints      = updatePos(updatePos(skinMeshPointsPos, selShapePointsPos), basePointsPos)
    relPoints         = updatePos(updatePos(newCorrectivePointsPos, basePointsPos), offsetPoints)
    setMorphPoints(localMatrix, selectedMorphId, poseMorphTag, relPoints)
    # --------------------------------------------------------------------------
    correctiveMesh.Remove()
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, skinMesh)
    skinMesh[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 2
    doc.SetSelection(skinMesh, c4d.SELECTION_ADD)
    doc.SetSelection(poseMorphTag, c4d.SELECTION_ADD)
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